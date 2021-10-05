# Trabajo 6: Detector de fraudes

Un banco ha detectado algunas transacciones fraudulentas y pretende construir una herramienta que le permita monitorizar y actuar tan pronto como sea posible ante la detección de uno de estos fraudes. Este banco ha recopilado las transacciones realizadas durante el último mes y ha etiquetado aquellas que son fraudulentas.

El banco os pide:

* Realizar un análisis exploratorio de los datos detallando aquellos aspectos más relevantes que hayáis encontrado.
* Construir un modelo para detectar los fraudes que han ocurrido.
* Desarrollar un cuadro de mando con Dash que resuma los aspectos más relevantes que hayáis extraido en el análisis exploratorio, permita conocer cuales son los indicios más comunes de fraude y pueda evaluar si una nueva transacción es fraudulenta o no.

¿Qué recomendaciones basadas en los datos le daríais al banco para tomar medidas preventivas ante este problema?

## Información de las variables

* step: Unidad de tiempo en el mundo real (1 significa una hora, 744 son 30 días) 
* type: Tipo de transacción. (CASH-IN, CASH-OUT, DEBIT, PAYMENT and TRANSFER)
* amount: Cantidad de la transacción en moneda local.
* nameOrig: Cliente que empezó la transacción.
* oldbalanceOrg: Saldo inicial antes de la transacción.
* newbalanceOrig: Nuevo saldo tras la transacción.
* nameDest: Cliente receptor de la transacción. 
* oldbalanceDest: Saldo inicial del receptor antes de la transacción. Ten en cuenta que no hay información de los clientes que empiezan por M (Merchants)
* newbalanceDest - Nuevo saldo del receptor tras la transacción. Ten en cuenta que no hay información de los clientes que empiezan por M (Merchants)
* isFraud: Transacciones fraudulentas (1 fraude, 0 caso contrario)
* isFlaggedFraud: Intento ilegal de transferir más de 200.000 en una única transacción.
