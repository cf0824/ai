# import xlsxwriter
#
#
# workbook = xlsxwriter.Workbook('test.xlsx')
# worksheet = workbook.add_worksheet()
#
# for i in range(100000):
#     worksheet.write('A%s'%(i+1),str(i))
#
# workbook.close()



import xlrd

data = xlrd.open_workbook('test.xlsx')
sheet = data.sheet_by_index(0)
rows = sheet.nrows
print(rows)
for i in range(rows):
    print(i,sheet.cell(i,0).value)
