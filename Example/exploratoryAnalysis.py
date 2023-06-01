#######################################################
# Proyecto: iTravel                                   #
# Autores: Aparicio Morales, Álvaro Manuel            #
#          Kanaan Mohammed Suhail Najm                #
# Asignatura: Ingeniería y Ciencia de Datos II        #
# Máster Universitario en Ingeniería Informática      #
# Universidad de Málaga                               #
#######################################################
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import re
# Cargar los datos
df = pd.read_csv('dataset/flights.csv', nrows=5000)

# Una vez tenemos cargado nuestro dataset, vamos a proceder a comprender la información que posee
# Podemos tomar los primeros valores del dataset y estudiarlos, con la función .head() y .tail()que nos devuelven
# los 5 primero valores del dataset y los 5 últimos
print(df.head())
print(df.tail())
# Con esta información podemos observar diferentes variables como pueden ser, Origen del vuelo, destino, atrasos,
# Compañía aérea..., algunas de estas son categoricas pues podemos agrupar los vuelos en función de su origen , 
# destino, compañia.Además con las funcioens .info(), .describe() nos pueden ayudar a conocer más a fondo nuestro dataset.
# Por lo que nos planteamos si existen variables no útiles, o redundantes, duplicadas, existen nomenclaturas con 
# sentido o incluso valores no propios.
print(df.info())
print(df.isna().sum())
print(df.describe())
# Al trabajar el dataset, hay algunos vuelos cuyo valor de aeropuerto no es un acrónimo si no que se encuentra con un número que es el id, debido a la gran
# cantidad de volumen de datos, podemos permitinos desechar estos vuelos.
# Ver la distribución de los vuelos según la aerolínea
print(df['AIRLINE'].value_counts())

# Ver la distribución de los vuelos según el mes
print(df['MONTH'].value_counts())

index_to_delete = []
for index, row in df.iterrows():
    if(bool(re.search(r'\d',row['ORIGIN_AIRPORT']))):
        index_to_delete.append(index)
df = df.drop(index_to_delete)

df = df.drop("FLIGHT_NUMBER",axis=1)
df = df.drop("TAIL_NUMBER",axis=1)
df = df.drop("DEPARTURE_TIME",axis=1)
df = df.drop("DEPARTURE_DELAY",axis=1)
df = df.drop("TAXI_OUT",axis=1)
df = df.drop("WHEELS_OFF",axis=1)
df = df.drop("ELAPSED_TIME",axis=1)
df = df.drop("DISTANCE",axis=1)
df = df.drop("WHEELS_ON",axis=1)
df = df.drop("TAXI_IN",axis=1)
df = df.drop("ARRIVAL_TIME",axis=1)
df = df.drop("DIVERTED",axis=1)
df = df.drop("CANCELLED",axis=1)
df = df.drop("CANCELLATION_REASON",axis=1)
df = df.drop("SECURITY_DELAY",axis=1)
df = df.drop("LATE_AIRCRAFT_DELAY",axis=1)
df = df.drop("WEATHER_DELAY",axis=1)
df = df.dropna()
# Para poder comenzar a encontrar alguna relación significativa entre variables, podemos calcular la matriz de correlación 
# e imprimir el resultado
correlation_matrix = df.corr()
plt.figure(figsize=(10,8))  
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.savefig('correlation_matrix.jpeg')

df.boxplot(column='DEPARTURE_DELAY', by='AIRLINE')
plt.title('Retrasos de salida por aerolínea')
plt.suptitle('')  # Eliminación del título automático generado por pandas
plt.savefig('departure_delays_by_airlines.jpeg')

#Aerolinea con más vuelos
df['AIRLINE'].value_counts().plot(kind='bar')
plt.title('Número de vuelos por aerolínea')
plt.xlabel('Aerolínea')
plt.ylabel('Número de vuelos')
plt.show()
