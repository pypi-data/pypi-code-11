from selenium.webdriver.support.wait import WebDriverWait
from pscore.core.support.ps_wait import PSWait


class WebDriverExtensions(object):
    def wait_until(self, func, timeout, timeout_message):
        """

        :type self: selenium.webdriver.remote.webdriver.WebDriver
        """
        WebDriverWait(self, timeout).until(
            lambda method: func(), timeout_message)
        return self

    # NOTE:  We may be better creating a subclass of remote web driver and adding methods in as
    # a wrapper.
    @staticmethod
    def patch(driver):
        """

        :type driver: selenium.webdriver.remote.webdriver.WebDriver
        """
        driver.wait_until = WebDriverExtensions().wait_until
        driver.wait = PSWait(driver)
        return driver