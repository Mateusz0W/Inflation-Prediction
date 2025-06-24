import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error,mean_absolute_percentage_error

def plot_predicted_inflation(y, y_pred, year):
    plt.plot(np.arange(1,len(y)+1),y,label='prawdziwa wartość',marker='o')
    plt.plot(np.arange(1,len(y_pred)+1),y_pred,label='przewidywana wartość',marker='o',color='red')
    plt.xlabel('Miesiąc')
    plt.ylabel('Wartość')
    plt.title(f'Zmiana inflacji w {year}')
    plt.legend()
    plt.grid(True)
    plt.show()

def calculate_metrics(X, y, model):
    y_pred = model.predict(X)
    return model.score(X,y), mean_squared_error(y,y_pred), np.sqrt(mean_squared_error(y, y_pred)), mean_absolute_percentage_error(y, y_pred)

def print_table(columns, values):
    print("\t".join(columns))
    for row in values:
        for value in row:
            if type(value) == float:
                print(f'{value:.4f}\t', end="")
            else:
                print(f'{value}\t', end="")
        print('\b', end="")
        print('\n', end="")