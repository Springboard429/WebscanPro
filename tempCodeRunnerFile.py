    if not isinstance(page, dict):
            continue

        url = page.get("url")
        forms = page.get("forms_on_page", [])

        for form in forms:
            vulns = test_form(url, form, session, payloads)
            all_vulnerabilities.extend(vulns)