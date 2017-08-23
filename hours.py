#!/usr/bin/env python3
"""
hours.py by Neil Grogan, 2015

A script to fill in hours automatically in SAP NetWeaver Portal
"""
from selenium import webdriver
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import configparser
import os

TIMEOUT = 5

def main():
    # Setup
    config = read_config()
    driver = load_website(config['url'], "SAP NetWeaver Portal")
    wait = WebDriverWait(driver, TIMEOUT)

    # Action
    login_to_website(driver, config['username'], config['password'])
    wait_for_timesheet_table(driver, wait)

    fill_in_timesheet(driver)
    submit_and_confirm_timesheet(driver, wait)

    logoff_and_close(driver, wait)

def read_config():
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.realpath(__file__))
    config.read(path + '/hours.ini')
    return config['DEFAULT']

def load_website(url, title):
    config = read_config()
    profile = FirefoxProfile()
    proxy = Proxy()
    proxy.proxy_autoconfig_url = config['proxy_url']
    profile.set_proxy(proxy)
    driver = Firefox(firefox_profile=profile)
    driver.get(url)
    assert title in driver.title
    return driver

def login_to_website(driver, username, password):
    elem = driver.find_element_by_id("logonuidfield")
    elem.send_keys(username)
    elem = driver.find_element_by_id("logonpassfield")
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)

def wait_for_timesheet_table(driver, wait):
    # wait for ajax items to load
    elem = wait.until(EC.element_to_be_clickable((By.ID, 'L2N2')))
    elem.click()

    wait.until(EC.frame_to_be_available_and_switch_to_it('contentAreaFrame'))
    wait.until(EC.frame_to_be_available_and_switch_to_it('isolatedWorkArea'))

    # Wait until timesheet appears
    elem = wait.until(EC.presence_of_element_located(
        (By.ID, "aaaaKEBH.VcCatTableWeek.WORKDATE1_InputField.0")))

def fill_in_timesheet(driver):
    # Fill in days of the week with 8 hours each
    for i in range(1,6):
        elem = driver.find_element_by_id("aaaaKEBH.VcCatTableWeek.WORKDATE"+str(i)+"_InputField.0")
        elem.click()
        elem.clear()
        elem.send_keys('8')

def submit_and_confirm_timesheet(driver, wait):
    # Wait for javascript to digest our fast hours entry :)
    time.sleep(0.2)

    # Start to Click Review Button
    elem = driver.find_element_by_id("aaaaKEBH.VcCatRecordEntryView.ButtonNext")
    elem.click()

    # Click Save/Confirm
    elem = wait.until(EC.presence_of_element_located(
        (By.ID, "aaaaLBOD.VcGenericButtonView.Save_com_sap_xss_hr_cat_record_vac_review_VcCatRecordReview")))
    elem.click()

    # Wait until confirmation of save
    elem = wait.until(EC.presence_of_element_located(
        (By.ID, "aaaaLMJA.WDMsgBox.MessageArea-txt")))
    assert "Your data has been saved" or "No data was changed" in elem.text

def logoff_and_close(driver, wait):
    # Start logging off
    driver.switch_to.default_content() # get back out of iframe
    driver.find_element_by_css_selector("#buttonlogoff > span.button_inner").click() # Click logoff
    driver.find_element_by_css_selector("div.button_middle").click() # Click yes to logoff
    wait.until(lambda driver:driver.title.lower().startswith('home'))
    driver.close()
    
if __name__ == '__main__':
    main()

