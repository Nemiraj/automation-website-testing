from typing import List, Dict, Any, Tuple
from urllib.parse import urljoin
from playwright.async_api import Page
from backend.app.core.logging import logger
from backend.app.core.config import settings


class FormAnalyzer:
    async def discover_and_test_forms(
        self,
        page: Page,
        page_url: str,
        form_submission_mode: str = "validation_only"
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Discovers all forms on the page, tests client-side validation safely,
        inspects PHP form actions/methods, and returns (forms_data_list, issues_list).
        """
        discovered_forms: List[Dict[str, Any]] = []
        issues: List[Dict[str, Any]] = []

        try:
            raw_forms = await page.evaluate("""
                () => {
                    const forms = Array.from(document.querySelectorAll('form'));
                    return forms.map((form, idx) => {
                        let selector = 'form';
                        if (form.id) selector += '#' + form.id;
                        else if (form.className && typeof form.className === 'string') {
                            const c = form.className.split(' ').filter(x => x.trim())[0];
                            if (c) selector += '.' + c;
                        }
                        if (selector === 'form' && forms.length > 1) {
                            selector = `form:nth-of-type(${idx + 1})`;
                        }

                        const formRect = form.getBoundingClientRect();
                        const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
                        const fields = inputs.map(input => {
                            const id = input.id;
                            let labelText = '';
                            if (id) {
                                const lbl = document.querySelector(`label[for="${id}"]`);
                                if (lbl) labelText = lbl.innerText.trim();
                            }
                            if (!labelText && input.closest('label')) {
                                labelText = input.closest('label').innerText.trim();
                            }

                            const rect = input.getBoundingClientRect();
                            return {
                                tagName: input.tagName.toLowerCase(),
                                type: input.getAttribute('type') || (input.tagName.toLowerCase() === 'textarea' ? 'textarea' : input.tagName.toLowerCase() === 'select' ? 'select' : 'text'),
                                name: input.getAttribute('name') || '',
                                id: id || '',
                                required: input.hasAttribute('required') || input.getAttribute('aria-required') === 'true',
                                placeholder: input.getAttribute('placeholder') || '',
                                label: labelText,
                                value: input.value || '',
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            };
                        });

                        const submitBtn = form.querySelector('button[type=submit], input[type=submit], button:not([type=button]):not([type=reset])');

                        return {
                            selector: selector,
                            action: form.getAttribute('action') || '',
                            method: (form.getAttribute('method') || 'POST').toUpperCase(),
                            fields: fields,
                            hasSubmitButton: !!submitBtn,
                            formIdx: idx,
                            x: Math.round(formRect.x),
                            y: Math.round(formRect.y),
                            width: Math.round(formRect.width),
                            height: Math.round(formRect.height)
                        };
                    });
                }
            """)

            for f in raw_forms:
                selector = f["selector"]
                fields = f["fields"]
                has_submit = f["hasSubmitButton"]
                action = f["action"]
                method = f["method"]
                
                form_record = {
                    "selector": selector,
                    "action": action,
                    "method": method,
                    "fields": fields,
                    "has_submit_button": has_submit,
                    "has_validation": False,
                    "validation_results": {}
                }

                form_coords = {
                    "x": f.get("x", 0),
                    "y": f.get("y", 0),
                    "width": f.get("width", 300),
                    "height": f.get("height", 150),
                    "tag": "form"
                }

                # 1. Check submit button existence
                if not has_submit:
                    issues.append({
                        "category": "forms",
                        "severity": "medium",
                        "page_url": page_url,
                        "title": f"Form Missing Explicit Submit Button ({selector})",
                        "description": f"The form '{selector}' does not contain an explicit `<button type='submit'>` or `<input type='submit'>`.",
                        "why_it_matters": "Users might struggle to submit the form on mobile or screen reader devices without an obvious submit control.",
                        "recommendation": "Add a clear submit button with visible text (e.g. `<button type='submit'>Submit</button>`).",
                        "suggested_fix": f"Add a `<button type='submit'>` inside {selector}.",
                        "selector": selector,
                        "coordinates": form_coords,
                        "marker_type": "rectangle",
                        "evidence": {"form_selector": selector}
                    })

                # 2. Check input labeling
                unlabeled_fields = [fld for fld in fields if not fld.get("label") and not fld.get("placeholder") and fld.get("type") not in ("hidden", "submit", "button", "reset")]
                if unlabeled_fields:
                    first_unl = unlabeled_fields[0]
                    issues.append({
                        "category": "accessibility",
                        "severity": "high",
                        "page_url": page_url,
                        "title": f"Unlabeled Form Inputs in {selector} ({len(unlabeled_fields)} fields)",
                        "description": f"Form fields {[fld['name'] or fld['type'] for fld in unlabeled_fields]} lack an associated `<label>` tag or aria-label.",
                        "why_it_matters": "Assistive technologies cannot announce the purpose of unlabeled inputs to visually impaired users.",
                        "recommendation": "Associate each input with a `<label for='input_id'>` or provide `aria-label`.",
                        "suggested_fix": "Add `<label for='...'>` for each input element.",
                        "selector": selector,
                        "coordinates": {
                            "x": first_unl.get("x", form_coords["x"]),
                            "y": first_unl.get("y", form_coords["y"]),
                            "width": first_unl.get("width", 150),
                            "height": first_unl.get("height", 35),
                            "tag": "input"
                        },
                        "marker_type": "rectangle",
                        "evidence": {"unlabeled_fields": unlabeled_fields}
                    })

                # 3. Check for email field type validation
                for fld in fields:
                    name_lower = (fld.get("name") or "").lower()
                    if "email" in name_lower and fld.get("type") == "text":
                        issues.append({
                            "category": "forms",
                            "severity": "medium",
                            "page_url": page_url,
                            "title": f"Email Field Uses Generic 'text' Type ({fld.get('name') or selector})",
                            "description": f"Input named '{fld.get('name')}' is used for emails but has type='text' instead of type='email'.",
                            "why_it_matters": "type='email' provides built-in browser email validation and optimizes mobile virtual keyboards (showing @ and .com keys).",
                            "recommendation": "Change the input type to `type='email'`.",
                            "suggested_fix": f"Set `type='email'` on input[name='{fld.get('name')}'].",
                            "selector": f"{selector} input[name='{fld.get('name')}']",
                            "coordinates": {
                                "x": fld.get("x", 0),
                                "y": fld.get("y", 0),
                                "width": fld.get("width", 200),
                                "height": fld.get("height", 35),
                                "tag": "input"
                            },
                            "marker_type": "arrow",
                            "evidence": fld
                        })

                # 4. Check for action attribute & relative path sanity in PHP
                if not action:
                    form_record["validation_results"]["action_target"] = "Self / Current URL"
                else:
                    resolved_action = urljoin(page_url, action)
                    form_record["validation_results"]["resolved_action_url"] = resolved_action
                    if action.startswith("http://") and page_url.startswith("https://"):
                        issues.append({
                            "category": "forms",
                            "severity": "high",
                            "page_url": page_url,
                            "title": f"Mixed Content Form Submission ({selector})",
                            "description": f"Form on HTTPS page submits to insecure HTTP endpoint '{action}'.",
                            "why_it_matters": "Browsers will block or warn users against submitting data over insecure connections.",
                            "recommendation": "Update form action to use relative URL or HTTPS protocol.",
                            "suggested_fix": f"Change action='{action}' to HTTPS in {selector}.",
                            "selector": selector,
                            "evidence": {"action": action}
                        })

                # 5. Check required fields validation
                required_fields = [fld for fld in fields if fld.get("required")]
                if required_fields:
                    form_record["has_validation"] = True
                    form_record["validation_results"]["required_fields_count"] = len(required_fields)
                    form_record["validation_results"]["required_field_names"] = [f.get("name") for f in required_fields]

                discovered_forms.append(form_record)

        except Exception as e:
            logger.warning(f"Error testing forms on {page_url}: {e}")

        return discovered_forms, issues

