#!/bin/bash

# takes all files in CsvFiles/ directory and creates a table with the same name as the file

rm -f ~/GroceryDeals/LogFiles/.mysqlerror
echo "" > ~/GroceryDeals/LogFiles/.mysqlerror

#credentials file
MYSQL_ACCESS="~/mysql_access"
. $MYSQL_ACCESS
MYSQL="/usr/bin/mysql -u$MYSQL_USER -p$MYSQL_PASSWORD"

ERROR=0

for csvfile in ../CsvFiles/*; do
    # get only file name, without relative path
    filename=$(basename ${csvfile})
    # create table with this name
    $MYSQL -e "use grocerydb" -e "
              CREATE TABLE ${filename} (
                  Name varchar(255),
                  Price decimal(4,2),
                  Quantity integer(3),
                  Weight varchar(10),
                  Limit integer(5),
                  Each decimal(4,2),
                  AdditionalInfo varchar(255),
                  Points integer(10),
                  Promotion varchar(255),
                  StoreName varchar(255),
                  StoreAddress varchar(255),
                  StoreCity varchar(255),
                  StoreProvince varchar(255),
                  StorePostalCode varchar(10)
              );" >> ~/GroceryDeals/LogFiles/.mysqlerror 2>&1

    if [ $? -ne 0 ]; then
        ERROR=1
    fi

    # insert data from csv file into created table
    $MYSQL -e "use grocerydb" -e "
              LOAD DATA LOCAL INFILE ${csvfile}
              INTO TABLE ${filename}
              FIELDS TERMINATED BY ','
              LINES TERMINATED BY '\n';" >> ~/GroceryDeals/LogFiles/.mysqlerror 2>>&1

    if [ $? -ne 0 ]; then
        ERROR=1
    fi
done

if [ $ERROR -ne 0 ]; then
    BODY=$(echo -e "MySQL failed to upload the data. Here are the logs for MySQL:\n\n\n")
    BODY=${BODY}$(cat ~/GroceryDeals/LogFiles/.mysqlerror)
    echo -e ${BODY} | mail -s "GroceryDeals Failed to Upload" ${EMAIL}
fi


