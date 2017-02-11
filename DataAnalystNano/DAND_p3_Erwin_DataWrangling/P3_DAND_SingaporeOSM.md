
## Data Wrangling OpenStreetMap Data of Singapore

The purpose of this project is to audit, analyze and clean [Singapore OpenStreetMap (OSM) XML](https://s3.amazonaws.com/metro-extracts.mapzen.com/singapore.osm.bz2). After the data is cleaned, it will be transformed into a JSON format to be uploaded into a MongoDB Database.

OpenStreetMap view of Singapore: https://www.openstreetmap.org/relation/536780

An example of the Singapore OSM XML:
```xml
<node id="3205311761" visible="true" version="1" changeset="27032256" timestamp="2014-11-25T21:38:36Z" user="tandesmond" uid="2485698" lat="1.3081957" lon="103.8551761">
  <tag k="addr:city" v="Singapore"/>
  <tag k="addr:housenumber" v="641, #20-50"/>
  <tag k="addr:postcode" v="200641"/>
  <tag k="addr:street" v="Rowell Road"/>
  <tag k="phone" v="+65 6396 0609"/>
  <tag k="name" v="Por's house"/>
</node>
```

The database needs to be in the following JSON format:

```json
{"_id": "3205311761",
 "created": {"version": "1",
             "timestamp": "2014-11-25T21:38:36Z",
             "changeset": "27032256",
             "uid": "2485698",
             "user": "tandesmond"},
 "pos": [1.3081957, 103.8551761]
 "address": {"housenumber": "641, #20-50",
             "postcode": "200641",
             "street": "Rowell Road"},
 "name": "Por's house",
 "phone": "+65 6396 0609"}
```

## Section I - Data Auditing

The mother of all steps is to first import all the required libraries and define the OSM filename variable.


```python
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
from pymongo import MongoClient
import codecs
import json
import time
OSMFILE = "data/singapore.osm"
```

To have an overview understanding of the XML file, we will start by analyzing the types and occurences of elements in the XML file. This allows us to understand what are the important elements to focus on and what are the relationships among those elements.

The function **`count_tags()`** receives an input of a dataset filename and returns a dictionary with the element name as the key and its number of occurence as the value.


```python
def count_tags(filename):
        # YOUR CODE HERE
        tags = defaultdict(int)
        tree = ET.parse(filename)
        for line in tree.iter():
            tags[line.tag] = tags[line.tag] + 1
            
        return tags
```


```python
start_time = time.time()
tags = count_tags(OSMFILE)

#sort the tags dictionary by its value and assign it back to a list.
sorted_by_occurrence = [(key,tags[key]) for key in sorted(tags, key=tags.get, reverse=True) ]

print 'Element tags and occurrences of Singapore.osm:\n'
pprint.pprint(sorted_by_occurrence)

print('\n--- %s seconds ---' % (time.time() - start_time))
```

    Element tags and occurrences of Singapore.osm:
    
    [('nd', 1734689),
     ('node', 1403705),
     ('tag', 612441),
     ('way', 214512),
     ('member', 81691),
     ('relation', 2312),
     ('bounds', 1),
     ('osm', 1)]
    
    --- 17.0199999809 seconds ---
    

The most striking finding is that there are two elements that appear only once:
- `<bounds>`: defining the OSM boundary, such as max latitude-longitude and min latitude-longitude coordinates of the OSM file
- `<osm>`: defining metadata such as the version of the osm file

There are three 'building-block' elements representing the physical world:
-  `<node>`: representing the latitude and longitude of the earth's surface
- `<way>`: representing linear features such as river and roads. It also represents boundaries of areas such as buildings or forests.
- `<relation>`: representing relationship between two or more data elements (nodes, ways, and/or other relations). 

The other three elements:
- `<tag>`: describing the meaning of the particular element to which they are attached. For example, **`highway=residential`** defines the way as a road whose main function is to give access to people's homes.
- `<nd>`, `<member>` : child tags under `<way>` and `<relation>` respectively. they contain information that further describes the parent elements they are attached to. For example, `<nd>` may contain reference id that points to `<node>` describing the latitude and longitude of `<way>` element.

Next, we will investigate the variation of attributes in the dataset.

The function **`count_attrs()`** receives an input of a dataset filename and returns a dictionary with the attribute name as the key and its number of occurence as the value.


```python
def count_attrs(filename):
    attrs = defaultdict(int)
    for event, elem in ET.iterparse(filename, events=('start', 'end')):
        if event == 'end':
            for attr in elem.attrib:
                attrs[attr] += 1
    return attrs
```


```python
start_time = time.time()
attrs = count_attrs(OSMFILE)
sorted_by_occurrence = [(key,attrs[key]) for key in sorted(attrs, key=attrs.get, reverse=True) ]

print 'Element tags and occurrences of Singapore.osm:\n'
pprint.pprint(sorted_by_occurrence)

print('\n--- %s seconds ---' % (time.time() - start_time))
```

    Element tags and occurrences of Singapore.osm:
    
    [('ref', 1816380),
     ('timestamp', 1620530),
     ('version', 1620530),
     ('changeset', 1620529),
     ('uid', 1620529),
     ('user', 1620529),
     ('id', 1620529),
     ('lon', 1403705),
     ('lat', 1403705),
     ('k', 612441),
     ('v', 612441),
     ('type', 81691),
     ('role', 81691),
     ('maxlon', 1),
     ('generator', 1),
     ('minlat', 1),
     ('maxlat', 1),
     ('minlon', 1)]
    
    --- 27.3550000191 seconds ---
    

The important attributes here are 'k' and 'v' because they contain the information of `<tag>` describing the 3 'building-block' elements (node, way, relation) that were mentioned above.

For example:
```xml
<node id="4310528089" visible="true" version="1" changeset="40850743" timestamp="2016-07-19T08:41:53Z" user="서상범" uid="3836172" lat="1.3177194" lon="103.8525915">
  <tag k="amenity" v="restaurant"/>
  <tag k="name" v="빠꾸떼 갈비탕"/>
 </node>
```

In the example above, we can see that 'k' and 'v' describe the parent `<node>` as "amenity" and also describe the name of the amenity.

Naturally, the next step is to find out the types and the number of occurence of the 'k' and 'v' attributes.

The function **`count_keys()`** receives an input of a dataset filename and returns a dictionary with the 'k' attribute as the key and its number of occurence as the value.


```python
def count_keys(filename):
    keys = defaultdict(int)
    for event, elem in ET.iterparse(filename, events=('start', 'end')):
        if event == 'end':
            key = elem.attrib.get('k')
            if key:
                keys[key] += 1
    return keys
```


```python
start_time = time.time()
keys = count_keys(OSMFILE)
sorted_by_occurrence = [(key,keys[key]) for key in sorted(keys, key=keys.get, reverse=True) ]

print 'Keys and occurrence in Singapore.osm:\n'
pprint.pprint(sorted_by_occurrence[:100])

print('\n--- %s seconds ---' % (time.time() - start_time))
```

    Keys and occurrence in Singapore.osm:
    
    [('building', 116024),
     ('highway', 88188),
     ('name', 63616),
     ('source', 42642),
     ('addr:street', 31527),
     ('addr:city', 25329),
     ('addr:housenumber', 22720),
     ('addr:postcode', 20305),
     ('oneway', 18612),
     ('addr:country', 12453),
     ('amenity', 10201),
     ('garmin_type', 10084),
     ('catmp-RoadID', 7873),
     ('service', 6860),
     ('created_by', 6253),
     ('location', 4968),
     ('asset_ref', 4954),
     ('route_ref', 4906),
     ('surface', 4801),
     ('building:levels', 4475),
     ('landuse', 3999),
     ('access', 3624),
     ('ref', 3465),
     ('leisure', 3428),
     ('layer', 3422),
     ('natural', 3083),
     ('lanes', 2996),
     ('foot', 2888),
     ('bridge', 2746),
     ('type', 2353),
     ('bicycle', 2293),
     ('power', 2027),
     ('maxspeed', 1994),
     ('shop', 1920),
     ('residential', 1629),
     ('waterway', 1486),
     ('sport', 1421),
     ('man_made', 1369),
     ('building:part', 1332),
     ('website', 1296),
     ('barrier', 1259),
     ('name:en', 1169),
     ('place', 1159),
     ('tourism', 1117),
     ('railway', 1049),
     ('parking', 1042),
     ('name:zh', 1030),
     ('seamark:type', 953),
     ('cuisine', 896),
     ('religion', 885),
     ('note', 876),
     ('phone', 874),
     ('horse', 857),
     ('motorcar', 848),
     ('operator', 789),
     ('hgv', 769),
     ('goods', 757),
     ('addr:housename', 748),
     ('tunnel', 727),
     ('lit', 721),
     ('psv', 714),
     ('height', 708),
     ('emergency', 705),
     ('route', 680),
     ('taxi', 680),
     ('garmin_road_class', 674),
     ('building:use', 654),
     ('golf', 640),
     ('aeroway', 617),
     ('building:colour', 598),
     ('covered', 573),
     ('motor_vehicle', 553),
     ('network', 551),
     ('public_transport:version', 543),
     ('sidewalk', 542),
     ('from', 540),
     ('to', 540),
     ('direction', 533),
     ('alt_name', 509),
     ('name:ms', 506),
     ('roof:colour', 474),
     ('water', 471),
     ('wheelchair', 462),
     ('opening_hours', 453),
     ('level', 450),
     ('building:material', 448),
     ('fixme', 422),
     ('building:min_level', 406),
     ('crossing', 371),
     ('width', 369),
     ('public_transport', 366),
     ('seamark:name', 362),
     ('area', 354),
     ('is_in:country', 350),
     ('school', 339),
     ('restriction', 337),
     ('roof:shape', 337),
     ('wikipedia', 325),
     ('is_in:state', 316),
     ('seamark:light:character', 316)]
    
    --- 23.3770000935 seconds ---
    

From the results above, we can see that there are mainly 5 formats of the 'k' attribute:
- lowercase only, e.g. 'building', 'highway'
- lowercase letter with underscore ('\_'), e.g. 'public_transport', 'opening_hours'
- lowercase letter with one colon ('\:'), e.g. 'addr:street', 'addr:city'. The hierarchy of key is separated by semicolon. It means that 'addr' is the primary key, 'city' is the secondary key describing the 'addr'.
- lowercase letter with two colons ('\:'), e.g. 'seamark:light:character', 'seamark:light:colour'
- others

We will use functions with regex matching to check for those formats and also potentially problematic formats:
- 'lower': to check for lowercase letter and lowercase letter with underscore
- 'lower_colon': to check for lowercase letter with colon
- 'lower_two_colon': to check for lowercase letter with two colons
- 'problemchars': to check for potential problematic chars with invalid symbols or blank spaces in between


```python
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*\:([a-z]|_)*$')
lower_two_colon = re.compile(r'^([a-z]|_)*\:([a-z]|_)*\:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
```


```python
def key_type(element, keys):
    if element.tag == "tag":
        if problemchars.search(element.attrib['k']):
            keys['problemchars'].append(element.attrib['k'])       
        elif lower_colon.search(element.attrib['k']):
            keys['lower_colon'].append(element.attrib['k'])
        elif lower_two_colon.search(element.attrib['k']):
            keys['lower_two_colon'].append(element.attrib['k'])
        elif lower.search(element.attrib['k']):
            keys['lower'].append(element.attrib['k'])
        else:
            keys['other'] .append(element.attrib['k'])          
    return keys
```


```python
def process_map(filename):
    keys = {"lower": [], "lower_colon": [], "lower_two_colon": [],"problemchars": [], "other": []}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys
```


```python
start_time = time.time()
keys = process_map(OSMFILE)
sorted_by_occurrence = [(key,len(keys[key])) for key in sorted(keys, key=lambda k:len(keys[k]), reverse=True) ]

print 'Keys and occurrence in singapore.osm:\n'
pprint.pprint(sorted_by_occurrence)

print('\n--- %s seconds ---' % (time.time() - start_time))
```

    Keys and occurrence in singapore.osm:
    
    [('lower', 468682),
     ('lower_colon', 130858),
     ('other', 9818),
     ('lower_two_colon', 3079),
     ('problemchars', 4)]
    
    --- 27.0119998455 seconds ---
    

From the result above, we can see that there is still around 1.6% of the datasets in the 'other' and 'problemchars' category. This may signify some invalid format that needs to be corrected.

As such, we will print out each of the dictionary key-value pair to check if the result is as what we expected.


```python
print(keys['lower'][:100])
```

    ['ref', 'highway', 'created_by', 'created_by', 'ref', 'highway', 'ref', 'highway', 'ref', 'name', 'highway', 'created_by', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'ref', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'ref', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'created_by', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name', 'exit_to', 'highway', 'created_by', 'ref', 'name', 'exit_to', 'highway', 'ref', 'name']
    


```python
print(keys['lower_colon'][:100])
```

    ['name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:hi', 'name:ms', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:hi', 'name:ms', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:hi', 'name:ms', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:hi', 'name:ms', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:zh', 'name:en', 'name:hi', 'name:ms', 'name:zh', 'name:ar', 'name:en', 'name:zh', 'name:en']
    


```python
print(keys['lower_two_colon'][:100])
```

    ['seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:landmark:height', 'seamark:light:character', 'seamark:light:reference', 'seamark:radar_transponder:group', 'seamark:radar_transponder:category', 'seamark:light:group', 'seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:light:sequence', 'seamark:landmark:height', 'seamark:light:character', 'seamark:light:reference', 'seamark:light:group', 'seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:light:character', 'seamark:light:reference', 'seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:light:sequence', 'seamark:landmark:height', 'seamark:light:character', 'seamark:light:reference', 'seamark:radar_transponder:group', 'seamark:radar_transponder:category', 'seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:light:character', 'seamark:light:reference', 'seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:light:category', 'seamark:light:character', 'seamark:light:reference', 'seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:light:character', 'seamark:light:reference', 'seamark:light:colour', 'seamark:light:character', 'seamark:light:reference', 'seamark:light:colour', 'seamark:light:character', 'seamark:light:reference', 'seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:light:character', 'seamark:light:reference', 'seamark:light:reference', 'seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:topmark:shape', 'seamark:topmark:colour', 'seamark:light:character', 'seamark:light:reference', 'seamark:beacon_lateral:colour', 'seamark:beacon_lateral:height', 'seamark:beacon_lateral:system', 'seamark:beacon_lateral:category', 'seamark:light:group', 'seamark:light:range', 'seamark:light:colour', 'seamark:light:height', 'seamark:light:period', 'seamark:topmark:shape', 'seamark:light:character', 'seamark:beacon_lateral:colour', 'seamark:beacon_lateral:height', 'seamark:beacon_lateral:system', 'seamark:beacon_lateral:category', 'seamark:light:reference', 'seamark:beacon_lateral:shape', 'seamark:beacon_lateral:colour', 'seamark:beacon_lateral:system', 'seamark:beacon_lateral:category', 'seamark:light:group', 'seamark:light:range', 'seamark:light:height', 'seamark:light:period', 'seamark:topmark:shape']
    


```python
print(keys['other'][:100])
```

    ['naptan:Bearing', 'name:zh-yue', 'name:bat-smg', 'name:fiu-vro', 'name:map-bms', 'name:roa-rup', 'name:roa-tara', 'name:be-tarask', 'name:zh-min-nan', 'name:zh-classical', 'country_code_iso3166_1_alpha_2', 'name:zh-yue', 'name:bat-smg', 'name:map-bms', 'name:roa-rup', 'name:roa-tara', 'name:be-tarask', 'name:zh-min-nan', 'W111', 'W112', 'W113', 'W114', 'W115', 'W125A', 'W125B', 'W5A15', 'W5A18', 'W5A19', 'W5A21', 'W5A13B', 'W5A210', 'W5A211', 'W5A21C', 'W5A11K-M', 'W312', 'W314', 'W317', 'W318', 'W319', 'W3111', 'W315A', 'W315B', 'W3110C', 'W3110E', 'W3110F', 'W3112A', 'W3110_A', 'W3110A_B', 'T16213', 'T16214', 'W1201', 'W1212', 'W1213', 'W1218', 'SMA', 'T1A', 'W1114', 'W1121', 'W1122', 'W1111A', 'W1111B', 'W1112A', 'T2231', 'T2232', 'T2233', 'T2234', 'T2251', 'T2232A', 'T22430', 'T22515', 'T22617', 'W212', 'W213', 'W214', 'W215', 'W216', 'W217', 'W221', 'W211A', 'W211B', 'W211D', 'W1001', 'W1011', 'T15', 'T11A101', 'T11A201', 'T11A202', 'T11A203', 'T11A303', 'T11A311', 'T11A314', 'T11A317', 'T11A401', 'T11A402', 'T11A405', 'T11A408', 'T11A410', 'T11A411', 'T11A412', 'T11A413']
    


```python
print(keys['problemchars'])
```

    ['LT 7', 'Singapore Poly', 'GARAGE SOLAR ENERGY 1', 'race course']
    

From the results above, we can see that:

For 'lower', 'lower_colon', 'lower_two_colon', the result is the same as what we have expected.

The interesting finding is in 'other' and 'problemchars'. 
In 'others', we can see some interesting format:
- lowercase with hyphen ('-'), e.g. 'name:zh-yue', 'name:zh-classical'
- lowercase with multiple colons (':'), e.g. 'seamark:light:1:range', 'seamark:light:3:group'
- uppercase letters,e.g. 'Longitude', 'Latitude'
- letters with numeric characters: e.g. 'W1213', 'T1A'
- combination of different formats, e.g. 'Data_Dicti', 'fuel:octane_95'

In 'problemchars', we have caught 'k' values containing uppercases and also blank spaces.

To standardize those interesting formats, it will take lots of time and probably also high-level regex skills. As such, we will not be touching on it in this project.

## Section II: Problems in the OSM File and Writing Dataset to Database

Besides auditing the elements, attributes, and keys, we also need to analyze the contents of the 'key' element, in which there may be some inconsistent / unstandardized data format.

In this case, I obtained a small subset of the OSM file to find any potential issues. Some of the problems that I discovered include:
- Data from **other countries** (from Malaysia and Indonesia)
- Unstandardized **street name** abbreviations (such as Jl, Jln)
- Unstandardized **house numbers**
- Unstandardized **phone numbers**
- Invalid **postal codes** (Singapore postal codes should be 6 digits)
- Names in **other languages**, such as in Chinese, Malay, or even Korean

The regular expressions below are used to check on some of the aforementioned issues:
- phone_re: to check for unstandardized phone numbers
- housenumber_re: to check for unstandardized house numbers
- postcode_re: to check for invalid postal codes


```python
phone_re = re.compile(r'(60|65|\+60|\+65)?\D?(\d{4})\D?(\d{4})', re.IGNORECASE)
housenumber_re = re.compile(r'(\d+[a-z]?|#?\d{2}-\d{2}|blk \d+)', re.IGNORECASE)
postcode_re = re.compile(r'^\d{6}$')
```

We define the variables below for data cleaning and transformation:
- CREATED: for transformation of XML to JSON. This variables holds the key for the JSON data structure.
- expected: for the expected content of street/ address element. This will be used to check whether there is any strange or inconsistent street / address element
- mapping: dictionary for mapping out invalid/ inconsistent street element


```python
#Variables for data cleaning and data transformation

#for the creation information
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

#expected content of address element
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Walk", "View", "Valley", "Green", "Crescent", "Terrace", "road"]

#dictionary for mapping out invalid/ unstandardized street element
mapping = { 
            "Ave": "Avenue",
            "Rd." : "Road",
            "Rd" : "Road",
            "Jl." : "Jalan ",
            "Jl" : "Jalan",
            "Jln" : "Jalan",
            "Btk" : "Butik",
            "Upp" : "Upper"
            }
```

The function **`cleanName(name)`** checks for unstandardized address element according to the 'mapping' dictionary as defined above.


```python
# transforms unstandardized address element
def cleanName(name):
    for key,val in mapping.iteritems():
        name = re.sub(key,val, name) #if 'name' matches with 'key', substitute it with 'val'
 
    return name
```

The function **`cleanPhoneNumber(phone_number)`** checks for unstandardized phone numbers. This is done with adding the country code (+65) to the phone numbers, as well as by using regex 'phone_re' to check for invalid phone number format.


```python
#transforms unstandardized phone numbers
def cleanPhoneNumber(phone_number):
    
    #print phone_number
    if not phone_number:
        return 	

    phone_number = phone_number.replace(" ", "")
    phone_number = phone_number.replace("-", "")
    if len(phone_number) == 8 :
        phone_number = "+65" + phone_number 

    m = phone_re.search(phone_number)
    if not m:
        print "EXCEPTION phone Number: " +phone_number    
        return None
    else:
        return m.group()
```

The function **`cleanHouseNumber(house_number)`** checks for unstandardized house numbers. This is done by using regex to check whether the house has any block numbers, and also the consistency of the unit number formatting.


```python
#transforms unstandardized house numbers
def cleanHouseNumber(house_number):
    
    #print house
    if not house_number:
        return
    
    m = housenumber_re.search(house_number)
    if not m:
        print "EXCEPTION House Number: " +house_number
        return None
    else:
        return m.group()
```

The function **`cleanPostCode(postcode)`** checks for unstandardized postal codes. This is done by using regex to check whether the value of the postal codes are 6 characters long.


```python
def cleanPostCode(postcode):
    
    if not postcode:
        return None
    
    m = postcode_re.search(postcode.strip())
    if not m:
        print "EXCEPTION postcode: " +postcode
        return None
    else:
        return m.group()
```

The function **`cleanValue(tag)`** checks for unstandardized postal codes. This is done by using regex to check whether the value of the postal codes are 6 characters long.


```python
def cleanValue(tag):
    #print ":D"
     
    if is_streetName_or_name(tag):
        return cleanName(tag.attrib['v'])
    elif is_phone_number(tag):
        return cleanPhoneNumber(tag.attrib['v'])
    elif is_house_number(tag):
        return cleanHouseNumber(tag.attrib['v'])                    
    elif tag.attrib['k'] == "addr:postcode":
        return cleanPostCode(tag.attrib['v'])  
```

The functions below check 'k' attributes to see which 'k' types (e.g. street, phone) it belongs to.


```python
#check for the value of 'k' attributes
def is_streetName_or_name(elem):
    return (elem.attrib['k'] == "addr:street" or elem.attrib['k'] == "name")
def is_phone_number(elem):
    return (elem.attrib['k'] == "phone")
def is_house_number(elem):
    return (elem.attrib['k'] == "addr:housenumber")	
def is_source(elem):
    return (elem.attrib['k'] == "source")
```

The function **`inSingapore(tag)`** checks whether an area is within the Singapore city.


```python
def inSingapore(tag):
    
    if tag.get('k') == "addr:city" and tag.get('v') != 'Singapore':
        return False
    if tag.get('k') == "is_in:country" and tag.get('v') != 'Singapore'    :
        return False
    if tag.get('k') == "addr:country" and tag.get('v') != 'SG'    :
        return False        

    return True
```

The function **`shape_element(element)`** transforms OSM XML to the desired JSON format to be exported to MongoDB.


```python
def shape_element(element):
    node = {}
    if  element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node['id'] =  element.get('id')
        node['type'] =  element.tag 
        node['visible'] =  "true"
        node['names']={}
        node['address'] = {}
        node['node_refs'] =[]
        node['created']={}
        
        #get the element based on the key in CREATED dict
        for c in CREATED:
            node['created'][c] = element.get(c)
        
        #get the lat and long position
        if element.get('lat') and element.get('lon'):
            node['pos'] = [float(element.get('lat')),float(element.get('lon'))]
        
        #processing 'tag' children element
        for tag in element.iter('tag'):
            if not tag.get('k') or problemchars.search(tag.get('k')):
                continue
                
            #excluding areas belonging to Malaysia or Indonesia    
            if not inSingapore(tag) :
                return None
                
            tagKey = tag.get('k')
            #check for invalid tag that starts with a colon
            if tagKey.startswith(':'): 
                tagKey = tagKey[1:]           
            
            if tagKey.startswith('name:'): #check for names in other languages: zh, ms, en, in
                node['names'][tagKey[5:]] = tag.get('v')
            elif tagKey.startswith('alt_name:'): #check for the alternate name of an amenity
                node['names']['alt'] = tag.get('v')
            elif tagKey == 'name': #name of an amenity
                node['name'] = cleanValue(tag)               
            elif tagKey.startswith('addr:'): #address tag
                node['address'][tagKey[5:]] = cleanValue(tag)                            
            else:
                node[tagKey] = tag.get('v')	
                        
        #processing 'nd' children element under 'way' element
        for tag in element.iter('nd'):
            node['node_refs'].append(tag.get('ref'))

        return node 
    else:
        return None
```

The function **`process_map(file_in, pretty=False)`** write the transformed JSON data to MongoDB


```python
def process_map(file_in, pretty=False):
    file_out = "{0}.json".format(file_in)
    data = []
    client = MongoClient()
    db = client.final_project
    collection = db.singaporeOSM
    
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            
            el = shape_element(element)
            if el:
                data.append(el)

                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
                    
    collection.insert_many(data)    #write into mongodb    
    
    return data
```


```python
def run():
    process_map(OSMFILE)
```


```python
run()
```

    EXCEPTION House Number: Off upper Thomson
    EXCEPTION postcode: 29425
    EXCEPTION House Number: Salmart Batam
    EXCEPTION postcode: 135
    EXCEPTION House Number: Perguruan Vingtsun Batam
    EXCEPTION postcode: 29463
    EXCEPTION postcode: 29461
    EXCEPTION postcode: 29461
    EXCEPTION postcode: 29464
    EXCEPTION House Number: LPMI Batam
    EXCEPTION postcode: 29433
    EXCEPTION House Number: Warung Butik
    EXCEPTION House Number: BCS Mall
    EXCEPTION House Number: New Place Pub & Restaurant
    EXCEPTION postcode: Singapore 408564
    EXCEPTION House Number: Gbabe Fashions
    EXCEPTION House Number: CONG JAYA
    EXCEPTION House Number: Sentosa Island, Singapore
    EXCEPTION postcode: 29464
    EXCEPTION House Number: Xamthone Herbal
    EXCEPTION postcode: S118556
    EXCEPTION postcode: 29464
    EXCEPTION postcode: 80200
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81300
    EXCEPTION postcode: 81200
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 2424
    EXCEPTION House Number: B
    EXCEPTION postcode: S 278989
    EXCEPTION House Number: Ground floor
    EXCEPTION postcode: 81100
    EXCEPTION postcode: S120517
    EXCEPTION postcode: 05901
    EXCEPTION House Number: Pandai Batam
    EXCEPTION postcode: 80300
    EXCEPTION postcode: 81700
    EXCEPTION postcode: 81700
    EXCEPTION postcode: 81100
    EXCEPTION postcode: 80000
    EXCEPTION postcode: 81200
    EXCEPTION postcode: 81900
    EXCEPTION postcode: 81700
    EXCEPTION postcode: 81750
    EXCEPTION postcode: 80040
    EXCEPTION postcode: 81300
    EXCEPTION postcode: 81000
    EXCEPTION postcode: 81060
    EXCEPTION postcode: 79100
    EXCEPTION postcode: 81200
    EXCEPTION postcode: 81000
    EXCEPTION postcode: 81300
    EXCEPTION postcode: 81000
    EXCEPTION postcode: 81000
    EXCEPTION postcode: 81000
    EXCEPTION postcode: 81000
    EXCEPTION postcode: 81450
    EXCEPTION postcode: 81450
    EXCEPTION postcode: 81450
    EXCEPTION postcode: 88752
    EXCEPTION postcode: 81300
    EXCEPTION postcode: 81300
    EXCEPTION postcode: 81300
    EXCEPTION postcode: 81300
    EXCEPTION postcode: 81200
    EXCEPTION postcode: 81300
    EXCEPTION postcode: 81300
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 81200
    EXCEPTION postcode: 80000
    EXCEPTION postcode: 80000
    EXCEPTION postcode: 80000
    EXCEPTION postcode: 80000
    EXCEPTION postcode: 81200
    EXCEPTION postcode: 29466
    EXCEPTION postcode: 24961
    EXCEPTION postcode: 80000
    EXCEPTION postcode: 81200
    EXCEPTION postcode: 80150
    EXCEPTION postcode: 2222
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 29432
    EXCEPTION postcode: 80250
    EXCEPTION postcode: 81700
    EXCEPTION postcode: 80250
    EXCEPTION postcode: #B1-42
    EXCEPTION postcode: 81800
    EXCEPTION postcode: 29425
    EXCEPTION postcode: 29425
    EXCEPTION postcode: 81000
    EXCEPTION postcode: 80050
    EXCEPTION postcode: 80150
    EXCEPTION postcode: 81000
    EXCEPTION postcode: 80000
    EXCEPTION postcode: 81100
    EXCEPTION postcode: 437 437
    EXCEPTION postcode: S 642683
    EXCEPTION postcode: 80000
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: 80050
    EXCEPTION House Number: q
    EXCEPTION House Number: E
    EXCEPTION House Number: Singapore Home
    EXCEPTION postcode: 80739
    EXCEPTION postcode: 80464
    EXCEPTION postcode: 80463
    EXCEPTION postcode: 80800
    EXCEPTION postcode: Bukit Batok Street 25
    EXCEPTION House Number: ??
    EXCEPTION House Number: Ministry of Social and Family Development
    EXCEPTION postcode: 74
    EXCEPTION postcode: 05901
    EXCEPTION postcode: 81700
    EXCEPTION postcode: 81700
    EXCEPTION postcode: 29464
    EXCEPTION House Number: Blk x
    EXCEPTION House Number: Blk x
    EXCEPTION House Number: Blk x
    EXCEPTION House Number: Blk x
    EXCEPTION House Number: Blk x
    EXCEPTION postcode: 31
    EXCEPTION postcode: 79200
    EXCEPTION postcode: 79200
    EXCEPTION postcode: 79200
    EXCEPTION postcode: 79200
    EXCEPTION House Number: E
    EXCEPTION House Number: R
    EXCEPTION House Number: B
    EXCEPTION House Number: S
    EXCEPTION House Number: M
    EXCEPTION House Number: H
    EXCEPTION House Number: Q
    EXCEPTION House Number: C
    EXCEPTION House Number: J
    EXCEPTION House Number: F
    EXCEPTION House Number: N
    EXCEPTION House Number: D
    EXCEPTION House Number: K
    EXCEPTION House Number: G
    EXCEPTION House Number: L
    EXCEPTION House Number: A
    EXCEPTION House Number: P
    EXCEPTION postcode: 80000
    EXCEPTION postcode: 80000
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81210
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION postcode: 81310
    EXCEPTION House Number: B
    EXCEPTION House Number: E
    EXCEPTION House Number: G
    EXCEPTION House Number: K
    EXCEPTION House Number: A
    EXCEPTION House Number: C
    EXCEPTION House Number: J
    EXCEPTION House Number: D
    EXCEPTION House Number: F
    EXCEPTION House Number: H
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: <different>
    EXCEPTION postcode: 8100
    EXCEPTION postcode: 81310
    EXCEPTION House Number: Polo Club Restaurant & Bar
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 80400
    EXCEPTION postcode: 80050
    EXCEPTION postcode: 80050
    EXCEPTION postcode: 80150
    EXCEPTION postcode: 80150
    EXCEPTION postcode: 80250
    EXCEPTION postcode: 81100
    EXCEPTION postcode: 562
    EXCEPTION postcode: 80250
    EXCEPTION postcode: 80250
    EXCEPTION postcode: 81500
    EXCEPTION postcode: 80350
    EXCEPTION postcode: 80350
    EXCEPTION postcode: 80350
    EXCEPTION postcode: 80250
    EXCEPTION postcode: 81200
    EXCEPTION postcode: 642
    EXCEPTION postcode: 79250
    EXCEPTION postcode: 79250
    

## Section III: Overview of the Dataset

After writing the cleaned data into MongoDB, it's


```python
client = MongoClient()
db = client.final_project
collection = db.singaporeOSM
```


```python
#Number of documents
collection.find().count()
```




    1603885




```python
#Number of nodes
collection.find({"type":"node"}).count()
```




    1403235




```python
#Number of ways
collection.find({"type":"way"}).count()
```




    200605




```python
#Number of unique users
len(collection.distinct("created.user"))
```




    1749




```python
#top 5 contributing users
pipeline= [{"$group":{"_id":'$created.user',"count":{"$sum":1}}},{"$sort":{"count":-1}},{"$limit":5}]
result = collection.aggregate(pipeline)
pprint.pprint(list(result))
```

    [{u'_id': u'JaLooNz', u'count': 365639},
     {u'_id': u'berjaya', u'count': 104158},
     {u'_id': u'rene78', u'count': 79949},
     {u'_id': u'cboothroyd', u'count': 74181},
     {u'_id': u'Luis36995', u'count': 41869}]
    


```python
#Number of users that only posted once; _id in the output represents the postcount
pipeline = [{"$group":{"_id":"$created.user", "count":{"$sum":1}}},
            {"$group":{"_id":"$count", "num_users":{"$sum":1}}}, {"$sort":{"_id":1}},
            {"$limit":1}]
result = collection.aggregate(pipeline)
pprint.pprint(list(result))
```

    [{u'_id': 1, u'num_users': 480}]
    


```python
#Top 10 Amenities
pipeline = [{"$match":{"amenity":{"$exists":1}}},
            {"$group":{"_id":"$amenity", "count":{"$sum":1}}}, 
            {"$sort":{"count":-1}}, {"$limit":10}]
result = collection.aggregate(pipeline)
pprint.pprint(list(result))
```

    [{u'_id': u'parking', u'count': 2024},
     {u'_id': u'restaurant', u'count': 1502},
     {u'_id': u'place_of_worship', u'count': 886},
     {u'_id': u'school', u'count': 687},
     {u'_id': u'cafe', u'count': 392},
     {u'_id': u'fast_food', u'count': 359},
     {u'_id': u'taxi', u'count': 336},
     {u'_id': u'fuel', u'count': 331},
     {u'_id': u'swimming_pool', u'count': 273},
     {u'_id': u'toilets', u'count': 229}]
    


```python
#Top religions ranked by the count of its 'place_of_worship'
pipeline = [{"$match":{"amenity":{"$exists":1},
            "amenity":"place_of_worship"}},
            {"$group":{"_id":"$religion", "count":{"$sum":1}}},
            {"$sort":{"count":-1}}]
result = collection.aggregate(pipeline)
pprint.pprint(list(result))
```

    [{u'_id': u'muslim', u'count': 495},
     {u'_id': u'christian', u'count': 191},
     {u'_id': None, u'count': 97},
     {u'_id': u'buddhist', u'count': 71},
     {u'_id': u'hindu', u'count': 17},
     {u'_id': u'taoist', u'count': 8},
     {u'_id': u'jewish', u'count': 4},
     {u'_id': u'sikh', u'count': 3}]
    

Surprisingly, Muslim has the most number of 'place_of_worship' when the country most populous religion is Buddhism.


```python
#top 10 popular cuisine types
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"restaurant"}},
            {"$group":{"_id":"$cuisine", "count":{"$sum":1}}}, 
            {"$sort":{"count":-1}}, {"$limit":10}]
result = collection.aggregate(pipeline)
pprint.pprint(list(result))
```

    [{u'_id': None, u'count': 907},
     {u'_id': u'chinese', u'count': 116},
     {u'_id': u'japanese', u'count': 66},
     {u'_id': u'indian', u'count': 39},
     {u'_id': u'korean', u'count': 39},
     {u'_id': u'italian', u'count': 38},
     {u'_id': u'asian', u'count': 30},
     {u'_id': u'pizza', u'count': 27},
     {u'_id': u'regional', u'count': 26},
     {u'_id': u'seafood', u'count': 17}]
    

Interestingly, Japanese cuisines seems to be popular in Singapore.

## Section IV: Further Exploration

### Information appearing in arbitrary field that is not expected
There are instances, such as, phone number which appears in random field that is not expected to appear at. To resolve this situation, it is extremely complex because we may need to iterate through 'v' attribute for all tags. We may be able to use advanced regex to handle this issue, but it may not be fool proof as well. As such, it will be good to show the comparison of false positive or false negative for this issue.

### Alternative ways to verify data accuracy
The other way to improve the accuracy of the data is to verify latitude, longitude, street name, phone number, or post code with credible database such data.gov.sg or Google Map. The challenge here is that there may be conflicts when different data sources using different terminology but referring to the same entity. As such, we may apply prioritizing for data sources, in which we can choose to use which data source first in case of conflicts.

### Utilizing geospatial features in OSM
The power of Open Street Map is that there are latitude and longitudes tagged to various entities. As such, we can use it for geospatial query, such as:
- How many restaurants within 500 meter of a location?
- If someone wants to open a restaurant business, he/she can explore the number of competitors nearby.
- Property pricing exploration: which factors (distance to train station, schools, shopping malls) correlate to property prices? Of course, we will need to merge with additional data sources to get property prices.

All this can be implemented with [Turf.js](http://turfjs.org/) and [Leaflet](http://leafletjs.com/), and it can potentially become a very serious and long-term project.

## References

- https://github.com/ryancheunggit/Udacity/blob/master/P3/code.py
- https://www.openstreetmap.org/relation/536780
- https://en.wikipedia.org/wiki/Singapore
- https://en.wikipedia.org/wiki/Batam
- https://en.wikipedia.org/wiki/Johor_Bahru
