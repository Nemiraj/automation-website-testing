from urllib.parse import urlparse
from datetime import datetime
from typing import List
from .models import Website, ScanResult, TestCase, TestStep


class TestGenerator:
    @staticmethod
    def generate_tests(website: Website, scan_result: ScanResult) -> List[TestCase]:
        tests: List[TestCase] = []
        pages = scan_result.pages
        origin = f"{urlparse(website.url).scheme}://{urlparse(website.url).netloc}"

        test_counter = 1

        def gen_id() -> str:
            nonlocal test_counter
            tid = f"TEST-{str(test_counter).zfill(3)}"
            test_counter += 1
            return tid

        now = datetime.utcnow().isoformat() + "Z"

        # 1. Core Transaction / Purchase Journey
        product_page = next((p for p in pages if any(k in p.path.lower() for k in ['product', 'shop', 'item', 'movie', 'watch'])), None)
        cart_page = next((p for p in pages if any(k in p.path.lower() for k in ['cart', 'basket', 'checkout', 'subscribe'])), None)

        purchase_steps: List[TestStep] = [
            TestStep(
                id='STEP-1',
                order=1,
                action='navigate',
                targetDescription='Open Homepage',
                value=website.url,
                expectedResult='Homepage should load with HTTP 200 and visible navigation items'
            )
        ]

        if product_page:
            purchase_steps.append(TestStep(
                id='STEP-2',
                order=2,
                action='click',
                targetDescription='Click Products / Catalog link',
                selector='text="Products"',
                selectorStrategy='text',
                expectedResult='Product catalog listing page should open'
            ))
            purchase_steps.append(TestStep(
                id='STEP-3',
                order=3,
                action='click',
                targetDescription='Click Add to Cart / Watch button',
                selector='button:has-text("Add to Cart"), [data-testid="add-to-cart"], button:has-text("Buy")',
                selectorStrategy='role',
                expectedResult='Item should be added to cart with active feedback notification'
            ))

        if cart_page or product_page:
            order_num = len(purchase_steps) + 1
            purchase_steps.append(TestStep(
                id=f'STEP-{order_num}',
                order=order_num,
                action='click',
                targetDescription='Open Cart',
                selector='a[href*="cart"], button:has-text("Cart"), [data-testid="nav-cart"]',
                selectorStrategy='text',
                expectedResult='Cart drawer or page opens displaying selected items'
            ))

            order_num += 1
            purchase_steps.append(TestStep(
                id=f'STEP-{order_num}',
                order=order_num,
                action='click',
                targetDescription='Proceed to Checkout',
                selector='button:has-text("Checkout"), a[href*="checkout"], [data-testid="btn-checkout"]',
                selectorStrategy='text',
                expectedResult='Checkout page should open with payment form'
            ))

            order_num += 1
            purchase_steps.append(TestStep(
                id=f'STEP-{order_num}',
                order=order_num,
                action='click',
                targetDescription='Click Complete Payment',
                selector='button:has-text("Pay"), button:has-text("Complete Order"), [data-testid="btn-pay"]',
                selectorStrategy='role',
                expectedResult='Payment request succeeds and order confirmation page is displayed'
            ))

        tests.append(TestCase(
            id=gen_id(),
            projectId=website.projectId,
            websiteId=website.id,
            name='Customer Purchase Journey (Cart to Payment)',
            description='End-to-end customer transaction journey verifying catalog browsing, adding item to cart, navigating to checkout, and submitting payment.',
            category='user_journey',
            priority='P0',
            severity='CRITICAL',
            journeyName='Customer Purchase Journey',
            url=website.url,
            steps=purchase_steps,
            isAiGenerated=True,
            tags=['e-commerce', 'core-funnel', 'revenue-critical'],
            createdAt=now
        ))

        # 2. Authentication Flow: Valid Credentials
        login_page = next((p for p in pages if any(k in p.path.lower() for k in ['login', 'auth', 'signin'])), None)
        login_url = login_page.url if login_page else f"{origin}/login"

        auth_username = website.authConfig.testUsername if (website.authConfig and website.authConfig.testUsername) else 'admin@example.com'
        auth_password = website.authConfig.testPassword if (website.authConfig and website.authConfig.testPassword) else 'password123'

        tests.append(TestCase(
            id=gen_id(),
            projectId=website.projectId,
            websiteId=website.id,
            name='User Login — Valid Credentials',
            description='Verifies successful authentication with valid credentials and redirection to authorized account area.',
            category='authentication',
            priority='P1',
            severity='HIGH',
            journeyName='Authentication Journey',
            url=login_url,
            steps=[
                TestStep(
                    id='STEP-1',
                    order=1,
                    action='navigate',
                    targetDescription='Open Login page',
                    value=login_url,
                    expectedResult='Login form rendered with username and password fields'
                ),
                TestStep(
                    id='STEP-2',
                    order=2,
                    action='fill',
                    targetDescription='Enter Email / Username',
                    selector='input[type="email"], input[name*="user"], input[name*="email"], [placeholder*="Email"]',
                    selectorStrategy='placeholder',
                    value=auth_username,
                    expectedResult='Email input accepts valid format'
                ),
                TestStep(
                    id='STEP-3',
                    order=3,
                    action='fill',
                    targetDescription='Enter Password',
                    selector='input[type="password"], [placeholder*="Password"]',
                    selectorStrategy='placeholder',
                    value=auth_password,
                    expectedResult='Password field masked'
                ),
                TestStep(
                    id='STEP-4',
                    order=4,
                    action='click',
                    targetDescription='Click Sign In',
                    selector='button[type="submit"], button:has-text("Sign In"), button:has-text("Login")',
                    selectorStrategy='role',
                    expectedResult='User authenticated successfully and authorized area is opened'
                )
            ],
            isAiGenerated=True,
            tags=['auth', 'security', 'login'],
            createdAt=now
        ))

        # 3. Authentication Validation: Empty Password
        tests.append(TestCase(
            id=gen_id(),
            projectId=website.projectId,
            websiteId=website.id,
            name='User Login — Empty Password Validation',
            description='Ensures authentication form prevents submission with missing password and presents clear inline validation.',
            category='authentication',
            priority='P2',
            severity='MEDIUM',
            journeyName='Authentication Journey',
            url=login_url,
            steps=[
                TestStep(
                    id='STEP-1',
                    order=1,
                    action='navigate',
                    targetDescription='Open Login page',
                    value=login_url,
                    expectedResult='Login page renders'
                ),
                TestStep(
                    id='STEP-2',
                    order=2,
                    action='fill',
                    targetDescription='Enter Email Only',
                    selector='input[type="email"], input[name*="user"], input[name*="email"]',
                    selectorStrategy='placeholder',
                    value='testuser@example.com',
                    expectedResult='Email filled'
                ),
                TestStep(
                    id='STEP-3',
                    order=3,
                    action='click',
                    targetDescription='Submit with Empty Password',
                    selector='button[type="submit"], button:has-text("Sign In"), button:has-text("Login")',
                    selectorStrategy='role',
                    expectedResult='Submission is blocked and inline error "Password required" is displayed'
                )
            ],
            isAiGenerated=True,
            tags=['auth', 'validation'],
            createdAt=now
        ))

        # 4. Form Submission & Input Boundaries
        contact_page = next((p for p in pages if any(k in p.path.lower() for k in ['contact', 'feedback']) or p.formsCount > 0), None)
        if contact_page:
            tests.append(TestCase(
                id=gen_id(),
                projectId=website.projectId,
                websiteId=website.id,
                name='Contact & Inquiry Form Validation (Invalid Email & Missing Fields)',
                description='Tests form submission boundary values with invalid email syntax and asserts client validation feedback.',
                category='form',
                priority='P2',
                severity='MEDIUM',
                url=contact_page.url,
                steps=[
                    TestStep(
                        id='STEP-1',
                        order=1,
                        action='navigate',
                        targetDescription='Open Form page',
                        value=contact_page.url,
                        expectedResult='Form page loads with input controls'
                    ),
                    TestStep(
                        id='STEP-2',
                        order=2,
                        action='fill',
                        targetDescription='Enter Invalid Email format (no @domain)',
                        selector='input[type="email"], input[name*="email"]',
                        selectorStrategy='placeholder',
                        value='invalid-email-format',
                        expectedResult='Input holds invalid email string'
                    ),
                    TestStep(
                        id='STEP-3',
                        order=3,
                        action='click',
                        targetDescription='Click Submit button',
                        selector='button[type="submit"], button:has-text("Submit"), button:has-text("Send")',
                        selectorStrategy='role',
                        expectedResult='Form prevents submit and shows email format validation alert'
                    )
                ],
                isAiGenerated=True,
                tags=['forms', 'validation'],
                createdAt=now
            ))

        # 5. Search & Catalog Discovery Flow
        tests.append(TestCase(
            id=gen_id(),
            projectId=website.projectId,
            websiteId=website.id,
            name='Product & Content Search Flow',
            description='Verifies search input responsiveness, query execution, and display of filtered results without console errors.',
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
                    targetDescription='Open Search entry page',
                    value=website.url,
                    expectedResult='Page opens with search input visible'
                ),
                TestStep(
                    id='STEP-2',
                    order=2,
                    action='fill',
                    targetDescription='Type query "Pro"',
                    selector='input[type="search"], input[placeholder*="Search"], [name="q"], [data-testid="search-input"]',
                    selectorStrategy='placeholder',
                    value='Pro',
                    expectedResult='Search input populated with text query "Pro"'
                ),
                TestStep(
                    id='STEP-3',
                    order=3,
                    action='click',
                    targetDescription='Click Search button',
                    selector='button:has-text("Search"), [data-testid="search-btn"], button[type="submit"]',
                    selectorStrategy='role',
                    expectedResult='Search action executes'
                ),
                TestStep(
                    id='STEP-4',
                    order=4,
                    action='assert_text',
                    targetDescription='Verify matching search items or feedback',
                    value='Pro',
                    expectedResult='Search results list dynamically updates to show matching items'
                )
            ],
            isAiGenerated=True,
            tags=['search', 'discovery'],
            createdAt=now
        ))

        # 6. Navigation & Route Health Verification
        nav_steps = [
            TestStep(
                id=f'STEP-{idx + 1}',
                order=idx + 1,
                action='navigate',
                targetDescription=f'Navigate to {p.title or p.path}',
                value=p.url,
                expectedResult=f'Route {p.path} should load with HTTP 200 and valid DOM structure'
            )
            for idx, p in enumerate(pages[:4])
        ]

        tests.append(TestCase(
            id=gen_id(),
            projectId=website.projectId,
            websiteId=website.id,
            name='Internal Navigation & Link Integrity',
            description='Crawls key internal header and footer links to confirm all routes return HTTP 200 without 404/500 errors.',
            category='navigation',
            priority='P1',
            severity='HIGH',
            url=website.url,
            steps=nav_steps,
            isAiGenerated=True,
            tags=['navigation', 'broken-links'],
            createdAt=now
        ))

        return tests
