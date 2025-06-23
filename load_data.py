import pandas as pd
import numpy as np

# zwraca {(rok, miesiąc): ([inflacja z poprzednich 12 miesięcy względem grudnia 
# poprzedniego roku, inflacja z poprzednich 12 miesięcy względem poprzedzającego
# je miesiąca], inflacja względem grudnia poprzedniego roku)}
def load_inflation(filename="miesiecznewskaznikicentowarowiuslugkonsumpcyjnychod1982roku_3.csv",
                  pointer1="Grudzień poprzedniego roku = 100", pointer2="Poprzedni miesiąc = 100",
                   step = 12):
    result_data = pd.DataFrame()
    data = pd.read_csv(filename,encoding="cp1250", sep=";")
    data= data.drop(columns=["Nazwa zmiennej","Jednostka terytorialna","Flaga","Unnamed: 7","Unnamed: 8"])
    data=data[data["Rok"].astype(int) >= 1987]
    data_last_december = data[data['Sposób prezentacji'] == pointer1].reset_index(drop=True)
    data_last_month = data[data['Sposób prezentacji'] == pointer2].reset_index(drop=True)
    result_data["Rok"] = data_last_december["Rok"]
    result_data["Miesiąc"] = data_last_december["Miesiąc"]
    result_data["Wartość_grudzień_poprzedniego_roku"] = (
        data_last_december['Wartość'].str.replace(',', '.').astype(float))
    result_data["Wartość_poprzedni_miesiąc"] = (
        data_last_month['Wartość'].str.replace(',', '.').astype(float))
    result_data = result_data.sort_values(by=["Rok", "Miesiąc"], ascending=[False, False])
    result_data = result_data.reset_index(drop=True)
    keys = [(yyyy, mm) for yyyy, mm in zip(result_data["Rok"][:-step], result_data["Miesiąc"][:-step])]
    model_args1 = [list(result_data["Wartość_grudzień_poprzedniego_roku"])[i:i+step]
                   for i in range(1, len(result_data) - step)]
    model_args2 = [list(result_data["Wartość_poprzedni_miesiąc"])[i:i+step]
                   for i in range(1, len(result_data) - step)]
    model_args = [model_arg1 + model_arg2 for model_arg1, model_arg2 
                  in zip(model_args1, model_args2)]
    inflation_values = result_data["Wartość_grudzień_poprzedniego_roku"]
    return {key : (model_arg, inflation) for key, model_arg, inflation 
            in zip(keys, model_args, inflation_values)}

# zwraca {(rok, miesiąc): ([liczba bezrobotnych z poprzednich 12 miesięcy], 
# inflacja względem grudnia poprzedniego roku)}
def load_unemployed(step = 12, filename="Liczba bezrobotnych zarejestrowanych w latach 1990-2025.csv"):
    def convert_to_float(x):
        if isinstance(x, float) and np.isnan(x):
            return np.nan
        else:
            return float(str(x).replace(',', '.'))

    data = pd.read_csv(filename, encoding="cp1250", sep=";").to_numpy()
    result = {}
    years = data[:, 0]
    years_key = []
    for year in years:
        years_key += 12 * [year]
    data = data[:, 1:]
    values = []
    for year_data in data:
        values.extend(reversed([convert_to_float(value) for value in year_data]))
    for (i, value), year in zip(enumerate(values, start=1), years_key):
        if i >= len(values)-step:
            break
        key = (year, 13 - ((i-1) % 12 + 1))
        result[key] = values[i:i+step]
    return result

def load_building_price(filename='cena_1_m2_powierzchni_uzytkowej_budynku_mieszkalnego_oddanego_do_uzytkowania.csv',
                        step = 12):
    """
    Wczytuje cene 1m^2 powierzchni użytkowej budynku mieszkalnego.
    interpoluje wartości kwartalne do wartości miesięcznych.
    Zakres od 10.1998 - 03.2025

    Parameters:
    -----------
    filename: str 
        nazwa pliku
    step: int
        krok wstecz
    
    Returns:
    --------
    dict
        Klucze to krotki (Rok,Miesiąc) np: (2015,9) wartość to cena powierzchni użytkowej z step poprzednich miesięcy 
    """
    data = pd.read_csv(filename,encoding="cp1250",sep=';')

    data['data'] = pd.to_datetime(data['Rok'].astype(str) + 'Q' + data['Kwartal'].astype(str))
    data.set_index('data',inplace=True)
    monthly_dates = pd.date_range(
        start= data.index.min(),
        end= data.index.max()+pd.offsets.QuarterEnd(),
        freq='MS'
    )
    interpolated_data = data['Wartosc'].reindex(monthly_dates).interpolate(method='linear')
    interpolated_data = interpolated_data.sort_index()
    result ={}
    for i in range(step,len(interpolated_data)):
        value = interpolated_data.iloc[i-step:i].tolist()
        date = interpolated_data.index[i]
        key = (date.year,date.month)
        result[key] = value
    
    return result

def load_avarage_salary(filename='Przeciętne miesięczne wynagrodzenie w gospodarce narodowej w latach 1950-2024.csv',
                        step=12):
    """
    Wczytuje przeciętne miesięczne wynagrodzenie w zł.
    Interpoluje wartości roczne do wartości miesięcznych.
    Zakres od 01.1980 - 12.2024

    Parameters:
    -----------
    filename: str 
        nazwa pliku
    step: int
        krok wstecz
    
    Returns:
    --------
    dict
        Klucze to krotki (Rok,Miesiąc) np: (2015,9) wartość to przeciętne miesięczne wynagrodzenie w zł z step poprzednich miesięcy 
    """
    data = pd.read_csv(filename,sep=';')
    data['Przeciętne miesięczne wynagrodzenie w zł'] = data['Przeciętne miesięczne wynagrodzenie w zł'].str.replace(' ','').str.replace(',','.').astype(float)
    
    data['data']=pd.to_datetime(data['Rok'].astype(str)+'-01-01')
    data.set_index('data',inplace=True)
    monthly_dates = pd.date_range(
        start= data.index.min(),
        end= "2024-12-01",
        freq='MS'
    )

    interpolated_data = data['Przeciętne miesięczne wynagrodzenie w zł'].reindex(monthly_dates).interpolate(method='linear')
    interpolated_data = interpolated_data.sort_index()
    result ={}
    for i in range(step,len(interpolated_data)):
        value = interpolated_data.iloc[i-step:i].tolist()
        date = interpolated_data.index[i]
        key = (date.year,date.month)
        result[key] = value
    
    return result

if __name__ == "__main__":
    inflation_dict = load_inflation()
    target_inflation_dict = {key: inflation_dict[key][1] for key in inflation_dict}
    inflation_model_args_dict = {key: inflation_dict[key][0] for key in inflation_dict}
    unemployed_dict = load_unemployed()
    building_price_dict = load_building_price()
    avarage_salary_dict = load_avarage_salary()