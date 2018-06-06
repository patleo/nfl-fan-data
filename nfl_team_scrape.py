import os
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

# wait print function
def wait_notice(wait_time):
    print('wait ' + str(wait_time) + ' seconds')
    for i in range(1, wait_time + 1):
        sleep(1)
        print('waited ' + str(i) + ' seconds')

# record program start time
program_epoch = datetime.now()

# list of teams to scrape; corresponds with url for each
team_list = ['ravens', 'buffalobills', 'bengals','browns','broncos','houstontexans','colts', 'jaguars','kcchiefs','miamidolphins', 'patriots', 'nyjets','raiders', 'steelers', 'chargers','tennesseetitans','azcardinals','atlanta_falcons','panthers','chicagobears','dallascowboys', 'lions', 'packers', 'vikings', 'saints','giants','eagles','49ers', 'seahawks', 'stlouisrams', 'tbbuccaneers', 'redskins']
total_teams = len(team_list)
print('total teams ' + str(total_teams))

scrape_count = 0
for t in team_list:
    # finished teams have a file named <team>_data.txt with all the data
    if os.path.isfile(t + '_data.txt'):
        total_teams -= 1
        if total_teams == 0:
            log_file.write('FINISHED')
            log_file.close()
            exit()
    else:
        scrape_epoch = datetime.now()
        file_name = t + '_temp.txt'
        data_file = open(file_name, 'w')
        log_file = open('log_file.txt', 'a')
        print('file created ' + file_name + '\n')
        log_file.write(t + ' scrape started\n')
        team_name = t
        print(str(total_teams) + " left")
        print('team to use ' + team_name )
        # create driver and get the url
        url = "https://interactive.twitter.com/nfl_followers2014/#?mode=team&team=" + team_name
        driver = webdriver.Firefox()
        driver.get(url)
        print('performed get ' + t)
        county_layer = driver.find_element_by_class_name("county-layer")
        print("loading county tiles locations")
        wait_notice(6)
        print("deleting beacon layer")
        driver.execute_script("return document.getElementsByClassName('beacon-layer')[0].remove();")
        print("beacon deleted")
        wait_notice(2)
        print("accessing county layer")
        tiles = county_layer.find_elements_by_class_name("tile")
        print("number of counties found" + str(len(tiles)))
        # iterates over county titles scraping data from HTML tooltip info
        tile_count = 0
        not_county_count = 0
        for tile in tiles:
            hover = ActionChains(driver).move_to_element(tile)
            hover.perform()
            sleep(.1)
            county = driver.find_element_by_xpath("//h3[contains(@class,'ng-binding') and contains(@class, 'ng-scope')]")
            county_name = county.text
            # detects non-county tiles
            if county.location['x'] == 0 and county.location['y'] == 0:
                print("not a county!\n")
                print(county.get_attribute("Style"))
                not_county_count += 1
                continue
            # catches NA for percent
            try:
                percent = driver.find_element_by_xpath("//span[contains(@class, 'ng-binding') and contains(@class, 'ng-scope')]")
                num = percent.text
            except NoSuchElementException:
                num = 'NA'
            # prints data to console and writes to data file
            print(county_name + " - " + num + "\n")
            data_file.write(county_name + "," + num + "\n")
            tile_count += 1
            # prints status update to console every 100 counties
            if tile_count % 100 == 0:
                print("********* " + str(tile_count) + " TILES SCRAPED *********")
                print("********* " + str(not_county_count) + " OF THOSE FAILED *********")
                print("********* " + str(datetime.now() - scrape_epoch) + " SCRAPE TIME *********")
                print("********* " + str(datetime.now() - program_epoch) + " PROGRAM TIME *********")

        total_teams -= 1
        # close: data file, log file, driver; print: program time log: program data
        data_file.close()
        new_file_name = team_name + '_data.txt'
        os.rename(file_name, new_file_name)
        log_file.write("tiles scraped = " + str(tile_count) + " county info failed = " + str(not_county_count)  + " scrape time = " + str(datetime.now() - scrape_epoch) + "\n\n")
        log_file.close()
        scrape_count += 1
        print(str(scrape_count) + ' teams scraped')
        print('closing driver')
        driver.close()
        print('program execution time so far ' + str(datetime.now() - program_epoch))
