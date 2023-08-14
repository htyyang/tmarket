# TMARKET: &nbsp;FETCH <span style="color: rgba(173, 216, 230, 1)">SOCCER PLAYERS'</span> DATA FROM <a href="https://www.transfermarkt.com" style="color: inherit;">https://www.transfermarkt.com</a>

## What is tmarket?
### A simple and useful Python package can help you get the data of a soccer player conveniently.

## Quick Start

### The Player module

The `Player` module, which allows you to create an object for a soccer player and get the data by calling its own methods.

```python
import tmarket as tm

# create an object for a player by providing its profile's url.
messi = tm.Player(url="https://www.transfermarkt.com/lionel-messi/profil/spieler/28003")

# get core info of the player "Messi"
messi.get_core_info()

# get the basic data of the player "Messi"
messi.get_basic_data()
```

Another simple usage
```python
import tmarket as tm

# create an object for a player by providing its profile's ID.
messi = tm.Player(id=28003)

# get core info of the player "Messi"
# "True" will make the method return the info in format of Pandas DataFrames
messi.get_core_info(df=True)

# get the basic data of the player "Messi"
# 1st "True" will make the method return the data in format of Pandas DataFrames
# 2nd "True" will filter all columns with considered missing values
messi.get_basic_data(df=True,drop_na=True)
```
Method to get the transfer history
```python
import tmarket as tm

# create an object for a player by providing its profile's ID.
messi = tm.Player(id=28003)

# show every section of transfer history
for history in messi.get_transfer_history():
    print(history) 
```



What I am trying to improve `Player` module in the next step:
1. Be able to create an `Player` object by a player's name. It will be achieved by automatically searching for profiles by the providing name.
2. Develop more methods for detail data, such as the number of goals in a specific year.
3. Improve the speed.

