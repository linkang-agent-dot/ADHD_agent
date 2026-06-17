# -*- coding: utf-8 -*-
"""直接往 RuleTips.xlsx 末尾追加1190行(绕开合并单元格,--from-tsv会炸)。"""
import io,sys,openpyxl
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
XLSX=r'C:\x3\gdconfig\data\RuleTips.xlsx'
TSVROW=open(r'C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_stage_v2\RuleTips_add.tsv',encoding='utf-8').read().rstrip('\n').split('\t')
wb=openpyxl.load_workbook(XLSX)
ws=wb['RuleTips'] if 'RuleTips' in wb.sheetnames else wb.active
# 找最后有数据的行(col A)
last=ws.max_row
while last>1 and (ws.cell(last,1).value is None or str(ws.cell(last,1).value).strip()==''):
    last-=1
r=last+1
for i,v in enumerate(TSVROW):
    if v=='' : continue
    cell=ws.cell(r,i+1)
    cell.value=int(v) if (i==0 and v.lstrip('-').isdigit()) else v
wb.save(XLSX);wb.close()
print(f"RuleTips.xlsx 追加行{r}: ID={TSVROW[0]} Tab={TSVROW[1]} Title={TSVROW[2]}")
