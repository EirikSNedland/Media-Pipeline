# Bulk Name Changer
Change filenames

## How to use manual
Enter the configuration in main file. 
* NAME_PREFIX new file name
* DEFAULT_SEASON needs to be set if the current filenames does not include season number
* LANGUAGE should be set if it is a .srt file 

The files to be changed needs to be added to the Items folder. Another option is to change the TARGET_DIRECTORY to the path of desired directory.

Save the file and run it from terminal.
Run in terminal:
```python .\renamer_script.py ```
 or
```py .\renamer_script.py ```


## How to use with docker compose
Enter config in compose file
* NAME_PREFIX 
* DEFAULT_SEASON 
* LANGUAGE 

Add files to items folder

Run in terminal:
```docker compose up --build```



## Testing
TestCases folder includes the test scenarioes the script was testet on. Add more if nessecary and copy over to items folder. Run script and see if it works as intended.

Make sure all files have prefix. The file in testdata that ends with .5 without .txt after will end up as "-part2.5" isntead of "-part2".
