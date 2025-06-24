import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import random

# łączy przekazane argumenty dla modelu we wskazanym zakresie lat. Oczekuje 
# słowników w postaci {(rok, miesiąc): [lista argumentów dla modelu]}
def combine_model_args(model_args1_dict, model_args2_dict, start_year, end_year):
    result_dict = {}
    for key in model_args1_dict:
        if (start_year <= key[0] <= end_year) and key in model_args2_dict:
            result_dict[key] = model_args1_dict[key] + model_args2_dict[key]
    return result_dict

# łączy słowniki postaci {(rok, miesiąc): [lista argumentów dla modelu]}, 
# {(rok, miesiąc): inflacja} w jeden o postaci 
# {(rok, miesiąc): ([lista argumentów dla modelu], inflacja)}
def add_target_inflations(model_args_dict, target_inflation_dict):
    result_dict = {}
    for key in model_args_dict:
        if key in target_inflation_dict:
            result_dict[key] = (model_args_dict[key], target_inflation_dict[key])
    return result_dict

# Zwraca dane podzielone na uczące i testowe ze znormalizowaną listą 
# argumentów dla modelu. Oczekuje słownika postaci{(rok, miesiąc): 
# ([lista argumentów dla modelu], docelowa wartość inflacji}
def normalize_and_split_data(model_args_and_inflation_dict, test_size=0.2):
    dict_values = model_args_and_inflation_dict.values()
    model_args_list = [value[0] for value in dict_values]
    inflation_list = [value[1] for value in dict_values]
    standard_scaler = StandardScaler()
    normalized_model_args_list = standard_scaler.fit_transform(model_args_list)
    X_train, X_test, y_train, y_test = train_test_split(normalized_model_args_list,
        inflation_list, test_size=test_size, random_state=123)
    return X_train, X_test, y_train, y_test

# Zwraca dane podzielone na uczące i testowe ze znormalizowaną listą 
# argumentów dla modelu. Oczekuje słownika postaci{(rok, miesiąc): 
# ([lista argumentów dla modelu], docelowa wartość inflacji}. Gwarantuje zachowanie
# kolejności chronologicznej danych
def normalize_and_split_data_chronologically(model_args_and_inflation_dict, test_size=0.2):
    model_args_and_inflation_dict = dict(sorted(model_args_and_inflation_dict.items()))
    dict_values = model_args_and_inflation_dict.values()
    model_args_list = [value[0] for value in dict_values]
    inflation_list = [value[1] for value in dict_values]
    standard_scaler = StandardScaler()
    normalized_model_args_list = standard_scaler.fit_transform(model_args_list)
    X_train = []
    X_test = []
    y_train = []
    y_test = []
    for args, inflation in zip(normalized_model_args_list, inflation_list):
        if random.random() < test_size:
            X_test.append(args)
            y_test.append(inflation)
        else:
            X_train.append(args)
            y_train.append(inflation)
    return X_train, X_test, y_train, y_test, standard_scaler

def prepare_inference_data(inference_data_dict, scaler):
    inference_data_dict = dict(sorted(inference_data_dict.items()))
    dict_values = inference_data_dict.values()
    model_args_list = [value[0] for value in dict_values]
    inflation_list = [value[1] for value in dict_values]
    normalized_model_args_list = scaler.transform(model_args_list)
    return normalized_model_args_list, inflation_list

def prepare_training_data(args_dict_tab, target_inflation_dict, start_year, end_year):
    if len(args_dict_tab) == 1:
        result = {}
        for key in args_dict_tab[0]:
            if (start_year <= key[0] <= end_year):
                result[key] = args_dict_tab[0][key]
    else:
        result = args_dict_tab[0]
        for i in range(1, len(args_dict_tab)):
            result = combine_model_args(result, args_dict_tab[i], start_year, end_year)
    result = add_target_inflations(result, target_inflation_dict)
    return result

# if __name__ == "__main__":
#     inflation_dict = load_inflation()
#     target_inflation_dict = {key: inflation_dict[key][1] for key in inflation_dict}
#     inflation_model_args_dict = {key: inflation_dict[key][0] for key in inflation_dict}
#     unemployed_dict = load_unemployed()
#     model_args_inflation_unemployed = combine_model_args(inflation_model_args_dict, 
#                                                         unemployed_dict, 1990, 2030)
#     inflation_unemployed_targets_dict = add_target_inflations(model_args_inflation_unemployed,
#                                                             target_inflation_dict)
#     X_train, X_test, y_train, y_test = normalize_and_split_data(inflation_unemployed_targets_dict)