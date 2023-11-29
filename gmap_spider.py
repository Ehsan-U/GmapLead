import time
from urllib.parse import quote_plus
import random
import hrequests
from pprint import pprint



class Spider():
    map_url = "https://www.google.com/maps/search/{}"


    def __init__(self):
        self.xhr_url = []
        self.session = hrequests.Session(
            browser=random.choice(['chrome', 'firefox']), 
            os=random.choice(['win', 'lin', 'mac'])
        )


    async def handle_request(self, route):
        request = route.request
        if 'search?tbm=map' in request.url:
            self.xhr_url.append(request.url)
        await route.continue_()


    def intercept_xhr(self, query):
        url = self.map_url.format(quote_plus(query))

        with self.session.render(url='https://www.google.com/', mock_human=True, headless=True) as page:
            browser = page.page

            page._call_wrapper(browser.route, "**/*", self.handle_request)
            page._call_wrapper(page._goto, url)
            page._call_wrapper(browser.focus, "//h1[text()='Results']/ancestor::div[contains(@aria-label, 'Results for')]")

            while True:
                time.sleep(2)
                last_element = browser.locator("//a[contains(@href, '/maps/place')]").last
                page._call_wrapper(last_element.scroll_into_view_if_needed)
                if self.xhr_url:
                    return self.xhr_url.pop()
        

    def search(self, query):
        xhr_url = self.intercept_xhr(query)
        print("Intercepted XHR URL:", xhr_url)




s = Spider()
s.search("developers in Bangalore")
s.search("developers in Lahore")
s.search("developers in Karachi")
# asyncio.run()

# await browser.locator("//div[@id='pane']/following-sibling::div//div[contains(@jsaction, 'focus: scrollable.focus')]").first.focus()
