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
def load_unemployed(target_inflation_dict, step = 12,
                    filename="Liczba bezrobotnych zarejestrowanych w latach 1990-2025.csv"):
    data = pd.read_csv(filename, encoding="cp1250", sep=";").to_numpy()
    result = {}
    years = data[:, 0]
    years_key = []
    for year in years:
        years_key += 12 * [year]
    data = data[:, 1:]
    values = []
    for year_data in data:
        values.extend(reversed(year_data))
    for (i, value), year in zip(enumerate(values, start=1), years_key):
        if i >= len(values)-step:
            break
        key = (year, 13 - ((i-1) % 12 + 1))
        result[key] = (values[i:i+step], target_inflation_dict[key])
    return result

if __name__ == "__main__":
    inflation_dict = load_inflation()
    target_inflation_dict = {key: inflation_dict[key][1] for key in inflation_dict}
    unemployed_dict = load_unemployed(target_inflation_dict)