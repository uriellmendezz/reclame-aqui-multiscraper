## Instructions to use the scraper from Reclame AQUI:

| **Argument** | **Required** | **Type** | **Help** | **Valid choices** | **Examples** | **Works for** |  
|-----------|-----------|--------------|-------|---------|---------|---------|
| ```-e``` *(--extract)* | Yes | str *(text)* | Section you want to extract. | ['company', 'companies', 'category', 'categories', 'rankings'] | ```-e 'category'```, ```-e 'categories'```, ```-e 'company'```, ```-e 'companies'```, ```-e 'rankings'```| - |
| ```-d``` *(--data)* | No | str *(text)* | Data you want to scrape. | ['last complains','problems','index evolution'] | ```-d 'last complains'```, ```-d ''problems''```, ```-d 'index evolution'``` | **['company']** |
| ```-l``` *(--link)* | No | str *(text)* | Category/Company link | <u>*https://www.reclameaqui.com.br/empresa/{company name}/*</u> and <u>*https://www.reclameaqui.com.br/segmentos/{segment name}/{category name}*</u> |*company link:*  ```-l 'https://www.reclameaqui.com.br/empresa/amazon/'```, *category link:*  ```-l 'https://www.reclameaqui.com.br/segmentos/beleza-e-estetica/higiene-pessoal/'```  | **['company', 'companies', 'category', 'categories']** |
| ```-o``` *(--output)* | Yes | str *(text)* | Output filename | *valid extensions:* *.csv  *.xlsx  *.xls| ```-o 'test-file.csv'```, ```-o 'test-file.xlsx'```, ```-o 'test-file.xls'```| **['company', 'companies', 'category', 'categories', 'rankings']** | 
| ```-f``` *(--filename)* | No | str *(text)* | Filename (to massive scrape). | *valid extensions:* *.csv  *.xlsx  *.xls| ```-f 'links-banks-companies.csv'```, ```-f 'links-beauty-companies-ranking.xlsx'```, ```-f 'best-companies-2023.xls'```| **['companies', 'categories']** | 

<br>

## Examples of usage.

**Extract the index evolution from an specific company.**
``` bash
python main.py -e 'company' -d 'index evolution' -l 'https://www.reclameaqui.com.br/empresa/amazon/' -o 'sample-amazon-index_evolution.csv'
```


``` bash
                  date  totalEvaluations  answered  ...  totalGeneralEvaluations status  companyShortname
0  2024-03-18T12:27:56             28889     56003  ...                      731  GREAT            amazon
1  2024-02-18T12:27:56             29291     54579  ...                      734  GREAT            amazon    
2  2024-01-18T12:27:56             30310     55246  ...                      702  GREAT            amazon    
3  2023-12-18T12:27:56             30570     54641  ...                      621  GREAT            amazon    
4  2023-11-18T12:27:56             27634     49173  ...                      516  GREAT            amazon    
5  2023-10-18T12:27:56             26293     47220  ...                      435  GREAT            amazon    
6  2023-09-18T12:27:56             24976     44740  ...                      360  GREAT            amazon    
7  2023-08-18T12:27:56             24893     44719  ...                      271  GREAT            amazon    
8  2023-07-18T12:27:56             23243     41799  ...                      161  GREAT            amazon    
9  2023-06-18T12:27:56             21589     39410  ...                       91  GREAT            amazon    

[10 rows x 16 columns]
```

<br>
<br>

**Extract the las complains from an specific company.**

``` bash
python main.py -e 'company' -d 'last compains' -l 'https://www.reclameaqui.com.br/empresa/amazon/' -o 'sample-amazon-complains.csv'
```


``` bash
               created                                        description  ...  companyId  companyShortname
0  2024-04-18T22:18:42  Realizei uma compra com data prevista de entre...  ...       7936            amazon  
1  2024-04-18T22:17:44  Tive assinatura Amazon Prime mensal por muito ...  ...       7936            amazon  
2  2024-04-18T22:14:26  Realizei a devolução do colchão no dia 28/03/2...  ...       7936            amazon  
3  2024-04-18T22:08:18  Boa noite, faz 9 dias que meu pedido está para...  ...       7936            amazon  
4  2024-04-18T22:07:14  Compramos um liquidificador em 13/02/2024, pag...  ...       7936            amazon  
5  2024-04-18T21:47:26  Comprei uma assistente virtual Eco dor geração...  ...       7936            amazon  
6  2024-04-18T21:44:34  Comprei um Livro pelo Marketplace da Amazon nã...  ...       7936            amazon  
7  2024-04-18T21:44:30  Não estou conseguindo acessar minha conta, fic...  ...       7936            amazon  
8  2024-04-18T21:37:52  Fiquei surpresa em descobrir esses dias que de...  ...       7936            amazon  
9  2024-04-18T21:31:42  Comprei cápsulas de cúrcuma com gengibre e foi...  ...       7936            amazon  

[10 rows x 8 columns]
```
<br>
<br>

**Extract the problems from an specific company.**


``` bash
python main.py -e 'company' -d 'problems' -l 'https://www.reclameaqui.com.br/empresa/amazon/' -o 'sample-amazon-problems.csv'
```

``` bash
                                 name  count  recorrencyPercentual          type companyId
0                Produto não recebido  49640                 17.90  problem_type      7936
1                   Cobrança indevida  25929                  9.35  problem_type      7936
2                   Atraso na entrega  23233                  8.38  problem_type      7936
3               Estorno do valor pago  19637                  7.08  problem_type      7936
4                 Propaganda enganosa  12784                  4.61  problem_type      7936
5                 Produto com defeito  12278                  4.43  problem_type      7936
6          Troca-Devolução de produto  11699                  4.22  problem_type      7936
7               Estorno do valor pago   9169                  3.31  problem_type      7936
8  Problemas na finalização da compra   6299                  2.27  problem_type      7936
9                         Login-Senha   5958                  2.15  problem_type      7936
```

<br>
<br>

**Extract data from an specific category.**

``` bash
python main.py -e 'category' -l 'https://www.reclameaqui.com.br/segmentos/eletroeletronicos/eletroeletronicos-acessorios/' -o 'sample-electronicos-category.csv'
```
```bash
         segmentName   segmentShortName  ... complainsCount companyPoints
0  Eletroeletrônicos  eletroeletronicos  ...             17   -513.714286
1  Eletroeletrônicos  eletroeletronicos  ...             23   -518.857143
2  Eletroeletrônicos  eletroeletronicos  ...            196    888.804170
3  Eletroeletrônicos  eletroeletronicos  ...            220   -754.952381
4  Eletroeletrônicos  eletroeletronicos  ...             31    450.348399
5  Eletroeletrônicos  eletroeletronicos  ...             22   -529.111111
6  Eletroeletrônicos  eletroeletronicos  ...             25    805.000000
7  Eletroeletrônicos  eletroeletronicos  ...            167    597.400000
8  Eletroeletrônicos  eletroeletronicos  ...            118   -275.800000
9  Eletroeletrônicos  eletroeletronicos  ...             26   -531.682540

[10 rows x 17 columns]
```

<br>

**Given an Excel file, extract data from various companies. The program will download three files**

``` bash
python main.py -e 'companies' -f 'example_input_data.xlsx' -o 'sample-from_excel-companies.csv'
```

```bash
Complains:

companyId         companyShortname  ...                                              title    status
0  2P4eLYj1gWaTiA5D  plenitude-distribuidora  ...                                Compra de um litro.  ANSWERED
1  2P4eLYj1gWaTiA5D  plenitude-distribuidora  ...                             Livro faltando páginas  ANSWERED
2  2P4eLYj1gWaTiA5D  plenitude-distribuidora  ...                               Produto não entregue  ANSWERED
3  2P4eLYj1gWaTiA5D  plenitude-distribuidora  ...                 Comprei o livro de HERNANES SANTOS  ANSW

Problems types:
                            name  count  recorrencyPercentual          type         companyId
0              Atraso na entrega    201                 54.32  problem_type  2P4eLYj1gWaTiA5D
1  Qualidade do serviço prestado     23                  6.22  problem_type  2P4eLYj1gWaTiA5D
2                 Produto errado     18                  4.86  problem_type  2P4eLYj1gWaTiA5D
3          Estorno do valor pago     18                  4.86  problem_type  2P4eLYj1gWaTiA5D
4                Mau Atendimento     15                  4.05  problem_type  2P4eLYj1gWaTiA5D
5            Produto com defeito     15                  4.05  problem_type  2P4eLYj1gWaTiA5D
6             Demora na execução     11                  2.97  problem_type  2P4eLYj1gWaTiA5D
7                 Livro faltando     10                  2.70  problem_type  2P4eLYj1gWaTiA5D
8                   Cancelamento      4                  1.08  problem_type  2P4eLYj1gWaTiA5D
9              Cobrança indevida      2                  0.54  problem_type  2P4eLYj1gWaTiA5D


Index evolution:
                date  totalEvaluations  ...  status         companyShortname
0  2024-03-18T01:55:30               122  ...  RA1000  plenitude-distribuidora
1  2024-02-18T01:55:30               117  ...  RA1000  plenitude-distribuidora
2  2024-01-18T01:55:30               117  ...  RA1000  plenitude-distribuidora
3  2023-12-18T01:55:30                78  ...  RA1000  plenitude-distribuidora
4  2023-11-18T01:55:30                54  ...  RA1000  plenitude-distribuidora
5  2023-10-18T01:55:30                44  ...   GREAT  plenitude-distribuidora
6  2023-09-18T01:55:30                42  ...   GREAT  plenitude-distribuidora
7  2023-08-18T01:55:30                49  ...   GREAT  plenitude-distribuidora
8  2023-07-18T01:55:30                47  ...   GREAT  plenitude-distribuidora
9  2023-06-18T01:55:30                52  ...  RA1000  plenitude-distribuidora

[10 rows x 16 columns]
```
<br>

**Extract current company ranking tables. Downloads and Excel file with multiple spredsheets (each one a ranking table)**

```bash
python main.py -e 'rankings' -o 'rankings-tables-xlsx'
```

```bash
   status      companyCreation  solvingRate  ...  mainSegment   secondarySegments  hasVerified
0   GREAT  2023-01-12T09:23:21        100.0  ...            9  [4ttEZI_ZlW4M-aIY]        False
1  RA1000  2014-10-28T13:57:00        100.0  ...           16                  []        False
2   GREAT  2021-05-03T19:19:44        100.0  ...            4                  []        False
3  RA1000  2009-07-02T10:22:00         98.4  ...           16  [Fqq7lNsvZxZHN-HA]        False
4  RA1000  2008-12-05T08:42:00         98.0  ...            5  [wSc0pBs0xq3zS4aR]        False
5   GREAT  2019-09-12T15:55:12         97.9  ...            3  [rBr47s_1-5ca6TcT]         True
6  RA1000  2009-10-27T11:37:00         98.9  ...            2                  []        False
7  RA1000  2020-05-07T08:38:49         99.0  ...            4                  []        False
8  RA1000  2021-04-29T10:11:39         99.2  ...            9  [oSilrbhvXd-1__C1]        False
9  RA1000  2010-05-14T15:38:00        100.0  ...           20  [MckKImFcBkMhvQtb]        False
```