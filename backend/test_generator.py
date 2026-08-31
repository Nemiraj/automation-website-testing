import os
import sys
from urllib.parse import urlparse
from datetime import datetime
from typing import List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from backend.models import Website, ScanResult, TestCase, TestStep
except ImportError:
    from models import Website, ScanResult, TestCase, TestStep


class TestGenerator:
    @staticmethod
    def generate_tests(website: Website, scan_result: ScanResult) -> List[TestCase]:
        tests: List[TestCase] = []
        pages = scan_result.pages or []
        origin = f"{urlparse(website.url).scheme}://{urlparse(website.url).netloc}"

        test_counter = 1

        def gen_id() -> str:
            nonlocal test_counter
            tid = f"TEST-{str(test_counter).zfill(3)}"
            test_counter += 1
            return tid

        now = datetime.utcnow().isoformat() + "Z"

        # 1. Navigation & Route Health Verification (All Discovered Pages)
        nav_steps: List[TestStep] = [
            TestStep(
                id='STEP-1',
                order=1,
                action='navigate',
                targetDescription=f'Open Homepage ({website.url})',
                value=website.url,
                expectedResult='Homepage should load with HTTP 200 and visible layout'
            )
        ]

        for idx, p in enumerate(pages[:6]):
            if p.url != website.url:
                nav_steps.append(TestStep(
                    id=f'STEP-{len(nav_steps) + 1}',
                    order=len(nav_steps) + 1,
                    action='navigate',
                    targetDescription=f'Verify Route: {p.path or p.url}',
                    value=p.url,
                    expectedResult=f'Page {p.path} should load with HTTP 200 without 404/500 errors'
                ))

        tests.append(TestCase(
            id=gen_id(),
            projectId=website.projectId,
            websiteId=website.id,
            name='Internal Navigation & Route Health Integrity',
            description='Crawls all key internal routes and static HTML pages to confirm HTTP 200 responses without broken links.',
            category='navigation',
            priority='P1',
            severity='HIGH',
            journeyName='Navigation & Link Health',
            url=website.url,
            steps=nav_steps,
            isAiGenerated=True,
            tags=['navigation', 'smoke', 'static-html'],
            createdAt=now
        ))

        # 2. Form Testing & Input Boundary Validation (Discovered Forms)
        form_pages = [p for p in pages if p.formsCount > 0 or any(e.inputType for e in p.elements)]
        if not form_pages and pages:
            form_pages = [pages[0]]

        for f_page in form_pages[:2]:
            inputs = [e for e in f_page.elements if e.inputType]
            email_input = next((e for e in inputs if e.inputType == 'email' or 'email' in (e.name or '').lower()), None)
            text_inputs = [e for e in inputs if e.inputType != 'hidden' and e.id != (email_input.id if email_input else '')]
            # Pick one concrete field to target for the fuzz test. A broad selector
            # list (e.g. "input[type=text], textarea, input:not([type=hidden])")
            # matches every text field on the page at once, which makes Playwright's
            # strict-mode fill() throw "resolved to N elements" and fail the test
            # even when the page is working perfectly fine.
            fuzz_target = text_inputs[0] if text_inputs else (email_input if email_input else None)
            if fuzz_target:
                fuzz_selector = (
                    f'[name="{fuzz_target.name}"]' if fuzz_target.name
                    else f'[placeholder="{fuzz_target.placeholder}"]' if fuzz_target.placeholder
                    else 'input[type="text"], textarea, input:not([type="hidden"])'
                )
            else:
                fuzz_selector = 'input[type="text"], textarea, input:not([type="hidden"])'

            # 2a. Form Happy Path
            happy_steps: List[TestStep] = [
                TestStep(
                    id='STEP-1',
                    order=1,
                    action='navigate',
                    targetDescription=f'Open Form Page ({f_page.path})',
                    value=f_page.url,
                    expectedResult='Form page renders with active inputs'
                )
            ]

            step_ord = 2
            if email_input:
                happy_steps.append(TestStep(
                    id=f'STEP-{step_ord}',
                    order=step_ord,
                    action='fill',
                    targetDescription=f'Fill Email ({email_input.name or "email"})',
                    selector=f'input[type="email"], [name="{email_input.name}"], [placeholder*="email"]',
                    selectorStrategy='placeholder',
                    value='qa.tester@example.com',
                    expectedResult='Valid email syntax accepted'
                ))
                step_ord += 1

            for ti in text_inputs[:2]:
                happy_steps.append(TestStep(
                    id=f'STEP-{step_ord}',
                    order=step_ord,
                    action='fill',
                    targetDescription=f'Fill {ti.name or ti.placeholder or "input"}',
                    selector=f'[name="{ti.name}"], [placeholder="{ti.placeholder}"], input[type="text"], textarea',
                    selectorStrategy='placeholder',
                    value='Sample Test Value',
                    expectedResult='Field accepts valid input'
                ))
                step_ord += 1

            happy_steps.append(TestStep(
                id=f'STEP-{step_ord}',
                order=step_ord,
                action='click',
                targetDescription='Submit Form',
                selector='button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Send")',
                selectorStrategy='role',
                expectedResult='Form processes submission without uncaught server errors'
            ))

            tests.append(TestCase(
                id=gen_id(),
                projectId=website.projectId,
                websiteId=website.id,
                name=f'Form Happy Path Submission ({f_page.title or f_page.path})',
                description='Submits valid synthetic data into all discovered form controls and verifies HTTP response code.',
                category='form',
                priority='P1',
                severity='HIGH',
                journeyName='Form Processing Journey',
                url=f_page.url,
                steps=happy_steps,
                isAiGenerated=True,
                tags=['forms', 'happy-path'],
                createdAt=now
            ))

            # 2b. Form Empty Required Validation
            tests.append(TestCase(
                id=gen_id(),
                projectId=website.projectId,
                websiteId=website.id,
                name=f'Form Empty Required Constraints ({f_page.title or f_page.path})',
                description='Submits empty fields to assert HTML5 required attributes and client validation alerts.',
                category='form',
                priority='P2',
                severity='MEDIUM',
                journeyName='Form Processing Journey',
                url=f_page.url,
                steps=[
                    TestStep(
                        id='STEP-1',
                        order=1,
                        action='navigate',
                        targetDescription=f'Open Form Page ({f_page.path})',
                        value=f_page.url,
                        expectedResult='Form page renders'
                    ),
                    TestStep(
                        id='STEP-2',
                        order=2,
                        action='click',
                        targetDescription='Click Submit with Empty Fields',
                        selector='button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Send")',
                        selectorStrategy='role',
                        expectedResult='Submission is blocked by browser HTML5 required validation'
                    )
                ],
                isAiGenerated=True,
                tags=['forms', 'validation'],
                createdAt=now
            ))

            # 2c. Form Security Fuzzing
            tests.append(TestCase(
                id=gen_id(),
                projectId=website.projectId,
                websiteId=website.id,
                name=f'Form Input Security Fuzzing ({f_page.title or f_page.path})',
                description='Tests special characters (<script>, quotes, unicode) to ensure sanitization without crash.',
                category='form',
                priority='P2',
                severity='MEDIUM',
                journeyName='Security & Fuzzing',
                url=f_page.url,
                steps=[
                    TestStep(
                        id='STEP-1',
                        order=1,
                        action='navigate',
                        targetDescription=f'Open Form Page ({f_page.path})',
                        value=f_page.url,
                        expectedResult='Form page renders'
                    ),
                    TestStep(
                        id='STEP-2',
                        order=2,
                        action='fill',
                        targetDescription='Inject Fuzz String in Input',
                        selector=fuzz_selector,
                        selectorStrategy='placeholder' if 'placeholder' in fuzz_selector else 'css',
                        value="<script>console.log('fuzz')</script>",
                        expectedResult='Input value set safely'
                    ),
                    TestStep(
                        id='STEP-3',
                        order=3,
                        action='click',
                        targetDescription='Submit Fuzzed Input',
                        selector='button[type="submit"], input[type="submit"], button:has-text("Submit")',
                        selectorStrategy='role',
                        expectedResult='Form safely sanitized without executing script or breaking DOM'
                    )
                ],
                isAiGenerated=True,
                tags=['forms', 'security', 'fuzzing'],
                createdAt=now
            ))

        # 3. Interactive Buttons & DOM Smoke Test
        buttons = [e for p in pages for e in p.elements if e.role == 'button' or e.tagName.upper() == 'BUTTON']
        if buttons:
            btn_steps: List[TestStep] = [
                TestStep(
                    id='STEP-1',
                    order=1,
                    action='navigate',
                    targetDescription='Open Homepage',
                    value=website.url,
                    expectedResult='Page loaded'
                )
            ]

            for b_idx, btn in enumerate(buttons[:3]):
                btn_steps.append(TestStep(
                    id=f'STEP-{b_idx + 2}',
                    order=b_idx + 2,
                    action='click',
                    targetDescription=f'Click Button: "{btn.accessibleName or btn.text or "Interactive Control"}"',
                    selector=btn.locators[0].selector if btn.locators else 'button',
                    selectorStrategy=btn.locators[0].strategy if btn.locators else 'css',
                    expectedResult='Button triggers action without throwing uncaught JavaScript console errors'
                ))

            tests.append(TestCase(
                id=gen_id(),
                projectId=website.projectId,
                websiteId=website.id,
                name='Interactive Buttons & Event Handlers Smoke Test',
                description='Triggers discovered buttons to ensure event handlers execute without runtime JavaScript crashes.',
                category='buttons',
                priority='P2',
                severity='MEDIUM',
                journeyName='Interactive Components',
                url=website.url,
                steps=btn_steps,
                isAiGenerated=True,
                tags=['buttons', 'smoke', 'javascript'],
                createdAt=now
            ))

        # 4. Search Flow (if search inputs or search query exists)
        has_search = any(any('search' in (e.name or '').lower() or 'search' in (e.placeholder or '').lower() for e in p.elements) for p in pages)
        if has_search:
            tests.append(TestCase(
                id=gen_id(),
                projectId=website.projectId,
                websiteId=website.id,
                name='Search Input & Discovery Flow',
                description='Tests search input responsiveness and query filtering without console errors.',
                category='search',
                priority='P2',
                severity='MEDIUM',
                journeyName='Search Journey',
                url=website.url,
                steps=[
                    TestStep(
                        id='STEP-1',
                        order=1,
                        action='navigate',
                        targetDescription='Open Search page',
                        value=website.url,
                        expectedResult='Page renders search controls'
                    ),
                    TestStep(
                        id='STEP-2',
                        order=2,
                        action='fill',
                        targetDescription='Enter Search Query "test"',
                        selector='input[type="search"], input[name*="search"], input[placeholder*="Search"]',
                        selectorStrategy='placeholder',
                        value='test',
                        expectedResult='Search query populated'
                    ),
                    TestStep(
                        id='STEP-3',
                        order=3,
                        action='click',
                        targetDescription='Submit Search Query',
                        selector='button:has-text("Search"), [data-testid="search-btn"], button[type="submit"]',
                        selectorStrategy='role',
                        expectedResult='Search query executes and returns filtered view'
                    )
                ],
                isAiGenerated=True,
                tags=['search'],
                createdAt=now
            ))

        return tests
