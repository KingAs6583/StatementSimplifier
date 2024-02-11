import pandas
import re

def list_str(data: list | str, by=True) -> str:
    """_summary_

    Args:
        data (list | str): Transaction Remarks are Description
        by (bool, optional): indicate to concate by or To. Defaults to True.
    Returns:
        str: string with conacte by or to of transaction Remarks
    """
    string = data
    if type(data) == list:
        string = ' | '.join(data)
    if by:
        return "By " + string
    else:
        return "To " + string
    
def __separate_nature__(string: str) -> str:
    """_summary_

    Args:
        string (str): Transaction Remarks are Description

    Returns:
        str: nature of transaction
    """
    words = string.split('/')
    
    if words[0].__contains__("RTGS-") or words[0].__contains__("NEFT-"):
        words[0] = ''.join(words[0].split('-')[0])

    for word in words:
        if len(word) <= 5:
            words = word
            break
    if type(words) == list:
        return ''
    return words


def __seperate_remarks_ids__(string : str):
    numbers = re.search(r"/(\d+)/", string)
    if numbers is not None:
        string = numbers.group(1)
    else:
        words = string.split('/')
        if words[0].__contains__("RTGS-") or words[0].__contains__("NEFT-"):
            string = words[0].split('-')[1]
        else:
            if len(words) > 2 and words[1].isalnum():
                string = words[1]
            else:
                return ''
    return string


def __string_op__(string: str):
    string = re.sub(r'/\d+', '', string)
    words = string.split('/')
    temp = string.split('/')

    for word in words:
        if len(word) <= 5:
            temp.remove(word)
            if word.__contains__("RTGS"):
                temp = temp[2]
                break
        if word.__contains__("Payment from"):
            temp.remove(word)

    if temp[0].__contains__("RTGS-") or temp[0].__contains__("NEFT-"):
        temp = temp[0].split('-')[2]
        # temp[0] = temp[0] privious 
    length = len(temp)
    if length > 1 and temp[length - 1].isalnum() and type(temp) == list:
        temp[length - 1] = ''
    if type(temp) == list and len(temp) > 2:
        temp = ' | '.join(temp)
    else:
        temp = ''.join(temp)
    return temp


def read_stmt(file: str) -> pandas.DataFrame:
    try:
        if file.endswith(".xlsx"):
            return pandas.read_excel(file, index_col=None)
        elif file.endswith(".csv"):
            return pandas.read_csv(file, index_col=None)
        else:
            print("file formate not support")
    except Exception as e:
        print("None Type Error")

class StatementSimplifier:
    """_summary_
    """

    def __init__(self, stmt: pandas.DataFrame) -> None:
        """_summary_

        Args:
            stmt (pandas.DataFrame): _description_
        """
        self.stmt = stmt

    @staticmethod
    def simplifer(data: pandas.DataFrame,transaction_col: str) -> pandas.DataFrame:
        """_summary_

        Args:
            data (pandas.DataFrame): _description_
            transaction_col (str): _description_

        Returns:
            pandas.DataFrame: _description_
        """
        data.insert(loc=data.columns.get_loc(transaction_col), column='Type', value=data[transaction_col].apply(__separate_nature__))
        data.insert(loc=data.columns.get_loc(transaction_col), column='UTR/RTGS/IMPS No', value=data[transaction_col].apply(__seperate_remarks_ids__))
        data[transaction_col] = data[transaction_col].apply(__string_op__)
        return data

    def simplifer(self,transaction_col: str) -> None:
        self.stmt.insert(loc=self.stmt.columns.get_loc(transaction_col), column='Type', value=self.stmt[transaction_col].apply(__separate_nature__))
        self.stmt.insert(loc=self.stmt.columns.get_loc(transaction_col), column='UTR/RTGS/IMPS No', value= self.stmt[transaction_col].apply(__seperate_remarks_ids__))
        self.stmt[transaction_col] = self.stmt[transaction_col].apply(__string_op__)

    def clean_data(self, deposite_col: str, withdrawal_col: str, balance_col: str, transaction_col: str,
                   remove_cols=None):
        if remove_cols is None:
            remove_cols = []
        self.stmt.drop(remove_cols, axis=1, errors='ignore', inplace=True)
        self.stmt[balance_col] = self.stmt[balance_col].astype(str)
        self.stmt[deposite_col] = self.stmt[deposite_col].str.replace(
            r"'|,", '', regex=True).astype(float)
        self.stmt[withdrawal_col] = self.stmt[withdrawal_col].str.replace(
            r"'|,", '', regex=True).astype(float)
        self.stmt[balance_col] = self.stmt[balance_col].str.replace(
            r"'|,", '', regex=True).astype(float)
        self.stmt.fillna(0, inplace=True)
        # data cleaning main col = Transaction Remarks
        # self.stmt[transaction_col] = self.stmt[transaction_col].apply(__string_op__)
        self.simplifer(transaction_col)

    def clean(self, amount_col: str, transaction_col: str,balance_col) -> None:
        self.stmt.insert(loc=self.stmt.columns.get_loc(balance_col),column="Debit (Withdraw)",value=self.stmt[amount_col].apply(self.__debit_op__))
        self.stmt.insert(loc=self.stmt.columns.get_loc(balance_col),column="Credit (Deposite)",value=self.stmt[amount_col].apply(self.__credit_op__))
        self.stmt[balance_col] = self.stmt[balance_col].str.replace(
            r"(Cr)", '').astype(str)
        # self.stmt[transaction_col] = self.stmt[transaction_col].apply(__string_op__)
        self.simplifer(transaction_col)

    @staticmethod
    def __debit_op__(number: str) -> float:
        if number.endswith("(Dr)") or number.endswith("Dr"):
            number = number.replace("(Dr)", '')
            return float(number)
        else:
            return 0

    @staticmethod
    def __credit_op__(number: str) -> float:
        if number.endswith("(Cr)") or number.endswith("Cr"):
            number = number.replace("(Cr)", '')
            return float(number)
        else:
            return 0

    def dr_cr(self, amount_col: str, indicator_col: str, transaction_col: str,balance_col) -> None:
        debit_col = self.stmt[self.stmt[indicator_col].isin(
            ['DR', 'Dr'])][amount_col].astype(str)
        self.stmt.insert(loc=self.stmt.columns.get_loc(balance_col),column="Debit (Withdraw)",value=debit_col)
        credit_col = self.stmt[self.stmt[indicator_col].isin(
            ['CR', 'Cr'])][amount_col].astype(str)
        self.stmt.insert(loc=self.stmt.columns.get_loc(balance_col),column="Credit (Deposite)",value=credit_col)
        self.simplifer(transaction_col)
        # self.stmt[transaction_col] = self.stmt[transaction_col].apply(__string_op__)
    
    def bankAc(self, date: str, transaction_col: str, deposite_col: str, withdrawal_col: str) -> pandas.DataFrame:
        data = self.stmt
        debit_side = data[~data[deposite_col].isin([0])]
        debit_side = debit_side[[date, transaction_col, deposite_col]]
        debit_side[transaction_col] = debit_side[transaction_col].apply(
            lambda x: list_str(x, False))
        debit_side.reset_index(drop=True, inplace=True)

        credit_side = data[~data[withdrawal_col].isin([0])]
        credit_side = credit_side[[date, transaction_col, withdrawal_col]]
        credit_side[transaction_col] = credit_side[transaction_col].apply(
            lambda x: list_str(x))
        credit_side.reset_index(drop=True, inplace=True)

        acc = pandas.concat([debit_side, credit_side], axis=1)
        acc.fillna('',inplace=True)
        return acc
