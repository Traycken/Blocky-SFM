from playwright.sync_api import sync_playwright
import os

def run_verify(page):
    path = "file://" + os.path.abspath("sfm-blockly-editor.html")
    page.goto(path)

    # 1. Add Trigger
    page.click("text=Trigger")
    page.wait_for_timeout(500)

    # 2. Drag Input from sidebar to the Trigger's zone
    # We'll use JavaScript to simulate the drag and drop because it's more reliable in headless
    page.evaluate('''() => {
        const triggerZone = document.querySelector(".zone");
        const inputBlock = document.querySelector(".pb-input");

        // Mock dragType
        window.dragType = "input";

        // Create events
        const dropEvent = new Event("drop", { bubbles: true });
        // We need to pass the zone items array to onZoneDrop.
        // In the real UI, it's bound via closure.
        // Let's just trigger the click on the button instead if drag-drop is hard to mock,
        // but the user specifically asked for drag and drop fix.
        // Actually, onZoneDrop is attached to the element.
    }''')

    # Let's try real Playwright drag and drop
    page.drag_and_drop(".pb-input", ".zone")
    page.wait_for_timeout(500)

    input_count = page.evaluate("blocks[0].children.filter(b => b.type === 'input').length")
    print(f"Inputs in trigger after drag-drop: {input_count}")

    if input_count == 0:
        raise Exception("Drag and Drop failed!")

    page.screenshot(path="verification_drag_drop.png")

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
