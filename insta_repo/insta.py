from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import random

class InstagramBot:

    def __init__(self, us, ps, max_likes = 1200):
        self._user = us
        self._pass = ps
        self._max_likes = max_likes
        self._wd = webdriver.Chrome('C:/webdrivers/chromedriver.exe')
        self._wd.set_window_size(1420, 800)
        self._new = []
        self._total_likes = 0

    def close(self):
        self._wd.close()

    def login(self):
        self._wd.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        self._wd.find_element_by_name('username').send_keys(self._user)
        self._wd.find_element_by_name('password').send_keys(self._pass)
        self._wd.find_element_by_xpath('//*[@class="_0mzm- sqdOP  L3NKy       "]').click()
        time.sleep(4)

    def goto_tag(self, tag):
        self._wd.get('https://www.instagram.com/explore/tags/' + tag + '/')
        print('On tag: ' + tag)
        time.sleep(5)

    def goto_act(self, act):
        self._wd.get('https://www.instagram.com/' + act + '/')
        print('At account ' + act)
        time.sleep(4)
    
    def select_first(self):
        self._wd.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div').click()
        time.sleep(2)
    
    def likeandfollow(self):
        if ',' not in self._wd.find_element_by_xpath('/html/body/div[3]/div[2]/div/article/div[2]/section[2]/div/div/button/span').text \
        and 'Like' == self._wd.find_element_by_xpath('/html/body/div[3]/div[2]/div/article/div[2]/section[1]/span[1]/button/span').get_attribute('aria-text'):
            self._wd.find_element_by_xpath('/html/body/div[3]/div[2]/div/article/div[2]/section[1]/span[1]/button').click()
            self._total_likes += 1
            print('Liked a photo')
            time.sleep(4)
            if random.randint(0, 10) < 2:
                self.follow()

    def next_photo(self):
        self._wd.find_element_by_link_text('Next').click()
        time.sleep(3)

    def follow(self):
        try:
            button = self._wd.find_element_by_xpath('//*[@class="oW_lN _0mzm- sqdOP yWX7d        "]')
        except:
            return
        if button.text == 'Follow':
            name = self._wd.find_element_by_xpath('/html/body/div[3]/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a').text
            button.click()
            self._new.append(name)
            print('Followed ' + name)
            time.sleep(10)

    def cycle_posts(self, val):
        try:
            self.select_first()
            while val > 0:
                self.likeandfollow()
                self.next_photo()
                print('Value: ' + str(val))
                val -= 1
        except:
            return

    def gather_hrefs(self, act):
        self.goto_act(act)
        self._wd.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').click()
        time.sleep(3)
        followers = self._wd.find_element_by_css_selector('div[role=\'dialog\'] ul')
        followers.click()
        actionChain = webdriver.ActionChains(self._wd)
        while len(followers.find_elements_by_css_selector('li')) < 500:
            try:
                followers.click()
                time.sleep(.4)
                actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()

                time.sleep(.4)
            except:
                break
        hrefs = []
        for user in followers.find_elements_by_css_selector('li'):
            try:
                hrefs.append(user.find_element_by_css_selector('a').get_attribute('href'))
            except:
                continue
        print('Gathered followers for ' + act + '\n' + str(hrefs))
        return hrefs

    def like_posts(self, act):
        if self._total_likes > self._max_likes:
            self.close()
            print('Maximum likes exceeded.')
            exit(1)
        try:
            # goto act
            self._wd.get(act)
            print('Now at "' + act + '"')
            time.sleep(2)
            # select first
            try:
                self._wd.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[2]/article/div/div/div[1]/div[1]/a/div[1]').click()
            except:
                self._wd.find_element_by_xpath('// *[@id="react-root"]/section/main/div/div[3]/article/div[1]/div/div[1]/div[1]/a/div[1]').click()
            time.sleep(2)
            count = 0
            while count < 3:
                # like post
                self._wd.find_element_by_xpath('/html/body/div[3]/div[2]/div/article/div[2]/section[1]/span[1]/button').click()
                self._total_likes += 1
                print('Liked post #' + str(self._total_likes))
                time.sleep(random.randint(8, 10))
                # next photo
                self._wd.find_element_by_link_text('Next').click()
                time.sleep(random.randint(6,8))
                count += 1
        except:
            return

    def cycle_tags(self, tags):
        for tag in tags:
            self.tag(tag)
    
    def cycle_people(self, people):
        for person in people:
            self.person(person)

    def tag(self, tag):
        self.goto_tag(tag)
        self.cycle_posts(50)

    def record_follows(self):
        self._new += list(pd.read_csv(self._user + '_users_followed_list.csv', delimiter=',').iloc[:, 1:2]['0'])
        df = pd.DataFrame(self._new)
        df.to_csv(self._user + '_users_followed_list.csv')
        print('Recorded follows.')

    def person(self, act):
        acts = self.gather_hrefs(act)
        for link in acts:
            self.like_posts(link)

def main():
    username = input('Username: ')
    password = input('Password: ')
    acts = input('Accounts (separate by ,): ').split(',')
    insta = InstagramBot(username, password, max_likes=1000)
    insta.login()

    insta.cycle_people(acts)

    '''
    while True:
        command = input("tag/tags/person/people: ")
        if command == 'person':
            insta.person(input('Account to go to: '))
        elif command == 'people':
            insta.cycle_people(input('Accounts (separate by ,): ').split(','))
        elif command == 'tag':
            insta.tag(input('Tag to go to: '))
        elif command == 'tags':
            insta.cycle_tags(input('Enter tags (separated by ,): ').split(','))
        else:
            break
    '''
    insta.close()
    insta.record_follows()
    exit(1)

if __name__=="__main__":
    main()
