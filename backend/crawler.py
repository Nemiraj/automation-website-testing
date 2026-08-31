import os
import sys
import asyncio
import hashlib
import re
import urllib.request
from urllib.parse import urlparse, urljoin
from typing import List, Set, Dict, Any, Optional
from datetime import datetime
from html.parser import HTMLParser

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from backend.models import ElementInfo, PageInfo, ScanResult, SiteMapNode
    from backend.locator import generate_locators_for_element
except ImportError:
    from models import ElementInfo, PageInfo, ScanResult, SiteMapNode
    from locator import generate_locators_for_element


class StaticHtmlParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.base_origin = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
        self.title = ""
        self.in_title = False
        self.internal_links: Set[str] = set()
        self.external_links: Set[str] = set()
        self.elements: List[Dict[str, Any]] = []
        self.form_count = 0
        self.current_form_action = ""
        self.current_form_method = "GET"

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): (v or "") for k, v in attrs}

        if tag_lower == 'title':
            self.in_title = True

        elif tag_lower == 'a':
            href = attr_dict.get('href', '').strip()
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                full_url = urljoin(self.base_url, href)
                try:
                    if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                        self.internal_links.add(full_url)
                    else:
                        self.external_links.add(full_url)
                except Exception:
                    pass

        elif tag_lower == 'form':
            self.form_count += 1
            self.current_form_action = attr_dict.get('action', '')
            self.current_form_method = attr_dict.get('method', 'POST').upper()

        elif tag_lower in ('input', 'textarea', 'select'):
            input_type = attr_dict.get('type', 'text').lower()
            if input_type != 'hidden':
                self.elements.push if False else self.elements.append({
                    'id': f"inp-{len(self.elements)}",
                    'tagName': tag.upper(),
                    'role': 'textbox' if input_type != 'checkbox' and input_type != 'radio' else input_type,
                    'inputType': input_type,
                    'placeholder': attr_dict.get('placeholder', ''),
                    'name': attr_dict.get('name', ''),
                    'idAttr': attr_dict.get('id', ''),
                    'ariaLabel': attr_dict.get('aria-label', ''),
                    'testId': attr_dict.get('data-testid', ''),
                    'action': self.current_form_action,
                    'method': self.current_form_method,
                    'required': 'required' in attr_dict,
                    'isInteractive': True,
                    'isDestructive': False
                })

        elif tag_lower == 'button' or attr_dict.get('role') == 'button' or (tag_lower == 'input' and attr_dict.get('type') in ('submit', 'button')):
            self.elements.append({
                'id': f"btn-{len(self.elements)}",
                'tagName': tag.upper(),
                'role': 'button',
                'accessibleName': attr_dict.get('aria-label') or attr_dict.get('value', ''),
                'text': attr_dict.get('value', ''),
                'idAttr': attr_dict.get('id', ''),
                'className': attr_dict.get('class', ''),
                'ariaLabel': attr_dict.get('aria-label', ''),
                'testId': attr_dict.get('data-testid', ''),
                'isInteractive': True,
                'isDestructive': False
            })

    def handle_endtag(self, tag: str):
        if tag.lower() == 'title':
            self.in_title = False
        elif tag.lower() == 'form':
            self.current_form_action = ""
            self.current_form_method = "GET"

    def handle_data(self, data: str):
        if self.in_title:
            self.title += data


class WebsiteCrawler:
    def __init__(
        self,
        root_url: str,
        website_id: str,
        max_depth: int = 3,
        max_pages: int = 15,
        same_origin_only: bool = True,
        headless: bool = True
    ):
        self.root_url = root_url.rstrip('/')
        self.website_id = website_id
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.same_origin_only = same_origin_only
        self.headless = headless
        self.visited_urls: Set[str] = set()
        self.pages_queue: List[Dict[str, Any]] = []
        self.discovered_pages: List[PageInfo] = []

    async def scan(self) -> ScanResult:
        try:
            from playwright.async_api import async_playwright
            return await self._scan_with_playwright()
        except Exception as e:
            print(f"[Crawler] Playwright note ({e}). Using robust Direct HTTP crawler for {self.root_url}...")
            return await self._scan_with_http()

    async def _scan_with_playwright(self) -> ScanResult:
        from playwright.async_api import async_playwright

        root_origin = f"{urlparse(self.root_url).scheme}://{urlparse(self.root_url).netloc}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebTestAI/1.0'
            )

            self.pages_queue.append({'url': self.root_url, 'depth': 0})

            while self.pages_queue and len(self.discovered_pages) < self.max_pages:
                current_item = self.pages_queue.pop(0)
                norm_url = self._normalize_url(current_item['url'])

                if norm_url in self.visited_urls:
                    continue
                self.visited_urls.add(norm_url)

                try:
                    page = await context.new_page()
                    page_info = await self._crawl_page(page, norm_url, current_item['depth'], root_origin)
                    self.discovered_pages.append(page_info)
                    await page.close()

                    if current_item['depth'] < self.max_depth:
                        for link in page_info.internalLinks:
                            n_link = self._normalize_url(link)
                            if n_link not in self.visited_urls and not any(self._normalize_url(q['url']) == n_link for q in self.pages_queue):
                                self.pages_queue.append({'url': n_link, 'depth': current_item['depth'] + 1})
                except Exception as err:
                    print(f"[Crawler] Error crawling {norm_url}: {err}")

            await browser.close()

        if not self.discovered_pages:
            return await self._scan_with_http()

        return self._finalize_scan_result()

    async def _crawl_page(self, page: Any, url: str, depth: int, root_origin: str) -> PageInfo:
        start_time = asyncio.get_event_loop().time()
        status_code = 200
        try:
            resp = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            if resp:
                status_code = resp.status
        except Exception:
            status_code = 0

        load_time_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

        title = url
        try:
            title = await page.title() or url
        except Exception:
            pass

        extracted = await page.evaluate(r'''(originStr) => {
            const internalLinks = [];
            const externalLinks = [];
            const elements = [];

            // 1. Links
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                if (!href || href.startsWith('javascript:') || href.startsWith('#')) return;
                try {
                    const parsed = new URL(href, window.location.href);
                    if (parsed.origin === originStr) {
                        if (!internalLinks.includes(parsed.href)) internalLinks.push(parsed.href);
                    } else {
                        if (!externalLinks.includes(parsed.href)) externalLinks.push(parsed.href);
                    }
                } catch(e){}
            });

            // 2. Buttons
            document.querySelectorAll('button, input[type="button"], input[type="submit"], [role="button"]').forEach((el, idx) => {
                const text = el.textContent?.trim() || el.value || '';
                const ariaLabel = el.getAttribute('aria-label') || '';
                const testId = el.getAttribute('data-testid') || '';
                const role = el.getAttribute('role') || 'button';
                const isDestructive = /delete|remove|cancel|destroy|clear|purge/i.test(text + ' ' + ariaLabel);

                elements.push({
                    id: `btn-${idx}`,
                    tagName: el.tagName,
                    role: role,
                    accessibleName: ariaLabel || text,
                    text: text,
                    idAttr: el.id,
                    className: el.className,
                    ariaLabel: ariaLabel,
                    testId: testId,
                    isInteractive: true,
                    isDestructive: isDestructive
                });
            });

            // 3. Forms & Inputs
            let formCount = 0;
            document.querySelectorAll('form').forEach((form, fIdx) => {
                formCount++;
                const formAction = form.getAttribute('action') || '';
                const formMethod = form.getAttribute('method') || 'GET';

                form.querySelectorAll('input, select, textarea').forEach((input, iIdx) => {
                    if (input.type === 'hidden') return;
                    elements.push({
                        id: `inp-${fIdx}-${iIdx}`,
                        tagName: input.tagName,
                        role: input.type === 'checkbox' ? 'checkbox' : input.type === 'radio' ? 'radio' : 'textbox',
                        inputType: input.type || 'text',
                        placeholder: input.placeholder || '',
                        name: input.name || '',
                        idAttr: input.id || '',
                        ariaLabel: input.getAttribute('aria-label') || '',
                        testId: input.getAttribute('data-testid') || '',
                        action: formAction,
                        method: formMethod,
                        required: input.hasAttribute('required'),
                        isInteractive: true,
                        isDestructive: false
                    });
                });
            });

            return { internalLinks, externalLinks, elements, formCount };
        }''', root_origin)

        processed_elements: List[ElementInfo] = []
        for el in extracted.get('elements', []):
            locators = generate_locators_for_element(el)
            processed_elements.append(ElementInfo(
                id=el.get('id', ''),
                tagName=el.get('tagName', ''),
                role=el.get('role'),
                accessibleName=el.get('accessibleName'),
                text=el.get('text'),
                inputType=el.get('inputType'),
                placeholder=el.get('placeholder'),
                name=el.get('name'),
                idAttr=el.get('idAttr'),
                className=el.get('className'),
                required=el.get('required', False),
                isInteractive=el.get('isInteractive', True),
                isDestructive=el.get('isDestructive', False),
                locators=locators
            ))

        buttons_count = len([e for e in processed_elements if e.role == 'button' or e.tagName.upper() == 'BUTTON'])
        inputs_count = len([e for e in processed_elements if e.tagName.upper() in ('INPUT', 'SELECT', 'TEXTAREA')])

        health_status = 'HEALTHY'
        if status_code >= 400 or status_code == 0:
            health_status = 'FAILED'
        elif load_time_ms > 4000:
            health_status = 'WARNING'

        path = urlparse(url).path or '/'
        page_id = f"PAGE-{hashlib.md5(path.encode()).hexdigest()[:8]}"

        return PageInfo(
            id=page_id,
            url=url,
            path=path,
            title=title,
            statusCode=status_code,
            loadTimeMs=load_time_ms,
            depth=depth,
            internalLinks=extracted.get('internalLinks', []),
            externalLinks=extracted.get('externalLinks', []),
            elements=processed_elements,
            formsCount=extracted.get('formCount', 0),
            buttonsCount=buttons_count,
            inputsCount=inputs_count,
            consoleErrorsCount=0,
            networkErrorsCount=0,
            healthStatus=health_status,
            lastScannedAt=datetime.utcnow().isoformat() + "Z"
        )

    async def _scan_with_http(self) -> ScanResult:
        """Robust direct HTTP crawler that works on any local XAMPP or remote URL without requiring browser binaries."""
        self.pages_queue.append({'url': self.root_url, 'depth': 0})

        while self.pages_queue and len(self.discovered_pages) < self.max_pages:
            current_item = self.pages_queue.pop(0)
            target_url = self._normalize_url(current_item['url'])

            if target_url in self.visited_urls:
                continue
            self.visited_urls.add(target_url)

            start_t = asyncio.get_event_loop().time()
            status_code = 200
            html_content = ""

            try:
                req = urllib.request.Request(
                    target_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebTestAI-HttpCrawler/1.0'}
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    status_code = response.getcode()
                    raw = response.read()
                    html_content = raw.decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"[Crawler HTTP] Notice on {target_url}: {e}")
                status_code = getattr(e, 'code', 500) if hasattr(e, 'code') else 500

            load_ms = int((asyncio.get_event_loop().time() - start_t) * 1000)

            parser = StaticHtmlParser(target_url)
            if html_content:
                try:
                    parser.feed(html_content)
                except Exception:
                    pass

            title = parser.title.strip() or target_url
            path = urlparse(target_url).path or '/'

            processed_elements: List[ElementInfo] = []
            for el in parser.elements:
                processed_elements.append(ElementInfo(
                    id=el['id'],
                    tagName=el['tagName'],
                    role=el.get('role'),
                    accessibleName=el.get('accessibleName'),
                    text=el.get('text'),
                    inputType=el.get('inputType'),
                    placeholder=el.get('placeholder'),
                    name=el.get('name'),
                    idAttr=el.get('idAttr'),
                    required=el.get('required', False),
                    isInteractive=True,
                    isDestructive=False,
                    locators=generate_locators_for_element(el)
                ))

            buttons_count = len([e for e in processed_elements if e.role == 'button' or e.tagName.upper() == 'BUTTON'])
            inputs_count = len([e for e in processed_elements if e.tagName.upper() in ('INPUT', 'SELECT', 'TEXTAREA')])

            page_info = PageInfo(
                id=f"PAGE-{hashlib.md5(path.encode()).hexdigest()[:8]}",
                url=target_url,
                path=path,
                title=title,
                statusCode=status_code,
                loadTimeMs=load_ms,
                depth=current_item['depth'],
                internalLinks=list(parser.internal_links),
                externalLinks=list(parser.external_links),
                elements=processed_elements,
                formsCount=parser.form_count,
                buttonsCount=buttons_count,
                inputsCount=inputs_count,
                consoleErrorsCount=0,
                networkErrorsCount=0,
                healthStatus='HEALTHY' if status_code < 400 else 'FAILED',
                lastScannedAt=datetime.utcnow().isoformat() + "Z"
            )
            self.discovered_pages.append(page_info)

            if current_item['depth'] < self.max_depth:
                for link in parser.internal_links:
                    n_link = self._normalize_url(link)
                    if n_link not in self.visited_urls and not any(self._normalize_url(q['url']) == n_link for q in self.pages_queue):
                        self.pages_queue.append({'url': n_link, 'depth': current_item['depth'] + 1})

        return self._finalize_scan_result()

    def _finalize_scan_result(self) -> ScanResult:
        now = datetime.utcnow().isoformat() + "Z"
        total_buttons = sum(p.buttonsCount for p in self.discovered_pages)
        total_forms = sum(p.formsCount for p in self.discovered_pages)
        total_inputs = sum(p.inputsCount for p in self.discovered_pages)
        total_links = sum(len(p.internalLinks) + len(p.externalLinks) for p in self.discovered_pages)

        root_page = next((p for p in self.discovered_pages if p.path == '/' or p.depth == 0), self.discovered_pages[0] if self.discovered_pages else None)
        tree = SiteMapNode(
            url=root_page.url if root_page else self.root_url,
            path=root_page.path if root_page else '/',
            title=root_page.title if root_page else 'Root',
            status=root_page.healthStatus if root_page else 'HEALTHY',
            children=[
                {
                    'url': p.url,
                    'path': p.path,
                    'title': p.title,
                    'status': p.healthStatus,
                    'children': []
                }
                for p in self.discovered_pages if root_page and p.id != root_page.id
            ]
        )

        return ScanResult(
            websiteId=self.website_id,
            rootUrl=self.root_url,
            scannedAt=now,
            totalPages=len(self.discovered_pages),
            totalLinks=total_links,
            totalButtons=total_buttons,
            totalForms=total_forms,
            totalInputs=total_inputs,
            pages=self.discovered_pages,
            siteMapTree=tree
        )

    def _normalize_url(self, url_str: str) -> str:
        try:
            u = urlparse(url_str)
            return f"{u.scheme}://{u.netloc}{u.path.rstrip('/')}{'?' + u.query if u.query else ''}"
        except Exception:
            return url_str
