# from fontTools.ttLib import TTFont
#
# #font = TTFont('base.woff')
# #font.saveXML('base.xml')
# font = TTFont('base.woff')
# #font.saveXML('maoyan.xml')
# print(font['glyf'].keys())
# # print(font['glyf']['uniEA5E'])
# list = font['cmap'].tables[0].ttFont.getGlyphOrder()
# list[1] = 'uni0078'
#
# utf8List = [eval(r"'\u"+uni[3:]+"'").encode("utf-8") for uni in list[1:]]
# utf8last = []
# print(utf8List)
# for i in range(len(utf8List)):
#     utf8List[i] = str(utf8List[i],encoding='utf-8')
#     utf8last.append(utf8List[i])
# print(utf8last)

print('asdf'.replace('g','a'))