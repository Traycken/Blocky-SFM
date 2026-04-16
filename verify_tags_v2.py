from playwright.sync_api import sync_playwright
import os

def run_verify(page):
    path = "file://" + os.path.abspath("sfm-blockly-editor.html")
    page.goto(path)

    # 1. Add a global tag
    page.fill("#newTagName", "MyTag")
    page.click("text=Add")
    page.wait_for_timeout(500)

    # 2. Add an Input block
    page.click("text=Trigger")
    page.wait_for_timeout(200)
    page.click("text=+ INPUT")
    page.wait_for_timeout(500)

    # 3. Use the tag picker via page.evaluate to ensure click happens correctly
    page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll(".tagbtn"));
        const myTagBtn = btns.find(b => b.textContent === "MyTag");
        if(myTagBtn) myTagBtn.click();
    }''')
    page.wait_for_timeout(500)

    label_value = page.evaluate("blocks[0].children[0].labels")
    print(f"Input block labels: '{label_value}'")

    if label_value != "MyTag":
        raise Exception("Tag picker failed!")

    page.screenshot(path="verification_tags_v2.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            run_verify(page)
        finally:
            context.close()
            browser.close()
