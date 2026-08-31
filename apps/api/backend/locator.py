import re
from typing import List, Dict, Any, Optional
from .models import GeneratedLocator


def generate_locators_for_element(el: Dict[str, Any]) -> List[GeneratedLocator]:
    locators: List[GeneratedLocator] = []

    test_id = el.get('testId') or el.get('data-testid')
    if test_id:
        locators.append(GeneratedLocator(
            strategy='testid',
            selector=f'[data-testid="{test_id}"]',
            confidence=0.99
        ))

    role = el.get('role')
    acc_name = (el.get('accessibleName') or el.get('text') or '').strip()
    if role and acc_name and len(acc_name) < 50:
        locators.append(GeneratedLocator(
            strategy='role',
            selector=f'role={role}[name="{acc_name}"]',
            confidence=0.95
        ))

    placeholder = el.get('placeholder')
    if placeholder:
        locators.append(GeneratedLocator(
            strategy='placeholder',
            selector=f'[placeholder="{placeholder}"]',
            confidence=0.90
        ))

    aria_label = el.get('ariaLabel') or el.get('aria-label')
    if aria_label:
        locators.append(GeneratedLocator(
            strategy='label',
            selector=f'[aria-label="{aria_label}"]',
            confidence=0.88
        ))

    text = el.get('text', '').strip()
    tag_name = el.get('tagName', '').upper()
    if text and tag_name in ('BUTTON', 'A', 'SPAN', 'P') and len(text) < 40:
        locators.append(GeneratedLocator(
            strategy='text',
            selector=f'text="{text}"',
            confidence=0.82
        ))

    id_attr = el.get('idAttr') or el.get('id')
    if id_attr and not re.match(r'^(react-|radix-|__next|ember|vue-|ng-)', id_attr, re.I):
        locators.append(GeneratedLocator(
            strategy='css',
            selector=f'#{id_attr}',
            confidence=0.80
        ))

    name = el.get('name')
    if name:
        locators.append(GeneratedLocator(
            strategy='css',
            selector=f'[name="{name}"]',
            confidence=0.75
        ))

    locators.append(GeneratedLocator(
        strategy='css',
        selector=tag_name.lower() or 'div',
        confidence=0.40
    ))

    return locators


def resolve_playwright_locator(page: Any, selector: str, strategy: Optional[str] = None) -> Any:
    """Resolves a selector string to a Playwright Python locator."""
    if strategy == 'role' and selector.startswith('role='):
        m = re.match(r'^role=([a-z0-9_-]+)\[name="(.+)"\]$', selector, re.I)
        if m:
            role, name = m.group(1), m.group(2)
            return page.get_by_role(role, name=name.strip())

    if strategy == 'placeholder' or selector.startswith('[placeholder='):
        m = re.search(r'\[placeholder="(.+)"\]', selector)
        if m:
            return page.get_by_placeholder(m.group(1))

    if strategy == 'label' or selector.startswith('[aria-label='):
        m = re.search(r'\[aria-label="(.+)"\]', selector)
        if m:
            return page.get_by_label(m.group(1))

    if strategy == 'testid' or selector.startswith('[data-testid='):
        m = re.search(r'\[data-testid="(.+)"\]', selector)
        if m:
            return page.get_by_test_id(m.group(1))

    if strategy == 'text' or selector.startswith('text='):
        m = re.search(r'^text="(.+)"$', selector)
        if m:
            return page.get_by_text(m.group(1))

    return page.locator(selector)


async def attempt_self_healing(page: Any, failed_selector: str, target_description: str) -> Optional[Dict[str, Any]]:
    """Self-healing locator fallback engine for Playwright Python."""
    clean_desc = re.sub(r'^(click|fill|select|check|submit)\s+', '', target_description, flags=re.I)
    clean_desc = clean_desc.replace('"', '').replace("'", "").strip()

    if len(clean_desc) > 1:
        # Strategy 1: Visible Text Search
        try:
            text_loc = page.get_by_text(clean_desc, exact=False).first
            if await text_loc.is_visible(timeout=1500):
                return {
                    'recovered_locator': text_loc,
                    'recovered_selector': f'text="{clean_desc}"',
                    'strategy': 'text',
                    'confidence': 0.85,
                    'reason': f'Found matching element by visible text content "{clean_desc}"'
                }
        except Exception:
            pass

        # Strategy 2: Button / Link Role Search
        try:
            btn_loc = page.get_by_role('button', name=clean_desc).first
            if await btn_loc.is_visible(timeout=1500):
                return {
                    'recovered_locator': btn_loc,
                    'recovered_selector': f'role=button[name="{clean_desc}"]',
                    'strategy': 'role',
                    'confidence': 0.90,
                    'reason': f'Found accessible button role with name "{clean_desc}"'
                }
        except Exception:
            pass

    return None
