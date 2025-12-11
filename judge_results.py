import pandas as pd
from enum import Enum
import os

class Order(Enum):
    ORDERED = 'Ordered'
    REVERSED = 'Reversed'
    SHUFFLED = 'Shuffled'

class JudgeResults:
    
    def __init__(self, filename='judge_results.csv'):
        self.CSV_FILE = filename

    def save_dataframe(self, df):
        """Save DataFrame to CSV"""
        df.to_csv(self.CSV_FILE, index=True)
        print(f"Saved data to {self.CSV_FILE}")
    
    def load_or_create_dataframe(self):
        """Load existing DataFrame or create new one"""
        # If we already have a saved dataframe, load it
        if os.path.exists(self.CSV_FILE):
            # Read CSV and set MultiIndex columns
            df = pd.read_csv(
                self.CSV_FILE,
                index_col=['Q ID', 'Ignore Order', 'Order Given'],
                dtype={
                    'Q ID': str,
                    'Ignore Order': str,
                    'Order Given': str,
                    'Score': int
                })
            print(f"Loaded existing data with {len(df)} combinations")
        # Otherwise, create a new dataframe
        else:
            # create an empty DataFrame with the correct columns
            df = pd.DataFrame(columns=['Score'])
            # Add the index columns, which are empty, and label them correctly
            df.index = pd.MultiIndex.from_arrays(
                [[], [], []],
                names=['Q ID', 'Ignore Order', 'Order Given'])
            print("Created new DataFrame")
        return df

    def add_score(self, qid: str, ignoreOrder: str, orderGiven: str, score: int):
        """Add a record to the simple DataFrame structure"""
        
        df = self.load_or_create_dataframe()
        
        index = (qid, ignoreOrder, orderGiven)
        # Add the record
        df.loc[index, "Score"] = score
        df.to_csv(self.CSV_FILE, index=True)
        print(f"Added record: QID {qid}, Score: {score}")
        self.save_dataframe(df)
        return df

    def show_data(self):
        print(self.load_or_create_dataframe())






# addScore('3216013', 'True', Order.REVERSED, 9)
# df = load_or_create_dataframe()

# print(df)
# questionIDs = [3216013, 60174]

# addScore('3216013', 'False', Order.SHUFFLED, 10)
# addScore('3216013', 'True', Order.REVERSED, 14)
# addScore('3216014', 'True', Order.REVERSED, 14)


#addScore('3216013', 'True', Order.REVERSED, 12)

#print(load_or_create_dataframe())