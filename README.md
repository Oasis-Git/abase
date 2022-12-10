# abase
This is one Database System designed by Oasis(Yuwei An). The database system is completed as the basic logic of SQL with Language Python.

## Function
1. Database layer command: USE, CREATE, DROP, SHOW, COLUMN OPERATION
2. Data layer command: INSERT, DELETE, UPDATE, SELECT
3. Advanced command: PRIMARY KEY OPERATION, INDEX OPERATION, JOIN OPERATION
4. Command Line DISPLAY

## Design
The database system includes:
### File_management
Mainly deal with file reading, writing and restore. The main management mode is page management, through (file name, page number) pairing to search and write pages. In this layer I used cache structure in which the temporary page is saved in the running memory, and used LLR method for page replacement. The page number we set is 2KB

### Record_management
Two classes are designed: The first one is RID which is responsible to store the page number and slot number. The second one is Record which is responsible to store the data in corresonding RID.

### Index_management
Here the whole RID of one dataset will form a B+ tree with key = primary key or ordered index. The B+ tree could be stored and dumped in JSON file and I used LLR method for main-memory/SSD exchange.

### Parser_management
Use antlr4 to translate the grammer of SQL to the code of visitor mode. 

### System_management
This part is the core management of design. The visitor.py inherit the visitor class in Parser_management and is respoinsible for the logical process of SQL command. It links the upper layer(command layer) and lower layer(restoration layer) and the mutual communication ny translation(encode, decode). 

### Result
The result of the command is implemented by class Result and class Error. The former includes msg, time and type, and the later includes the error information.
