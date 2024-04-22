from bs4 import BeautifulSoup
import pymongo
import re

def connectDatabase(): 
    try: 
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["cs4250"]
        return db
    except: 
        print("Database did not connect")


def parse_faculty_info(db):
    pages_collection = db["pages"]
    professors_collection = db["professors"]
    target_page = pages_collection.find_one({"url": "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"})
    soup = BeautifulSoup(target_page['html'], 'html.parser')

    faculty_list = soup.find_all('div', {'class':'clearfix'})

    for profProfile in faculty_list:
        if profProfile.img:
            website_tag = profProfile.find("a", string=re.compile("cpp.edu/"))
            website = website_tag['href'] if website_tag else website_tag.text.strip()

            profData = {
                "name": profProfile.h2.text,
                "title": profProfile.p.find("strong", string=re.compile("Title")).next_sibling.replace(":", "").strip(),
                "office": profProfile.p.find("strong", string=re.compile("Office")).next_sibling.replace(":", "").strip(),
                "phone": profProfile.p.find("strong", string=re.compile("Phone")).next_sibling.replace(":", "").strip(),
                "email": profProfile.p.find("a", string=re.compile("@cpp.edu")).text.strip(),
                "website": website
            }
            professors_collection.insert_one(profData)


def main():
    db = connectDatabase()
    parse_faculty_info(db)

main()