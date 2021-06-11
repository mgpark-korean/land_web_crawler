from parser.NaverLandParser import NaverLandParser

URL = 'https://new.land.naver.com/complexes?ms=37.3575749,127.1179303,16&a=APT:JGC:ABYG&e=RETAIL'

id_list = NaverLandParser.get_marker_id_list(URL)
NaverLandParser.parse_land_info(URL, id_list)