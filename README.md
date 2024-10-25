# ABIChallenge_DavidVillate

# AB InBev MLOps Challenge v7

## 1. Architecture

En un ecosistema empresarial moderno, la implementación y consumo eficiente de modelos analíticos requiere una arquitectura robusta que permita el manejo y procesamiento adecuado de datos desde diversas fuentes, garantizando la gobernanza y accesibilidad de los modelos desplegados para diferentes aplicaciones y usuarios finales. En esta arquitectura, Azure Data Factory (ADF) se encarga de la ingesta y orquestación de los datos, mientras que Databricks se posiciona como la plataforma central para el procesamiento y despliegue de modelos de machine learning, apoyado por Unity Catalog para la gestión de datos y seguridad.

<div align="left">
    <img src="Images/Architecture.png" width="50" height="50">
</div>

### Flujo de Trabajo
- Fuentes de Datos Externas e Internas: La arquitectura comienza con la ingesta de datos desde múltiples fuentes, tanto internas como externas. Estas fuentes incluyen bases de datos on-premises, archivos Excel, APIs, redes sociales, y sensores IoT, entre otras. Estos datos son gestionados y transferidos mediante Azure Data Factory, que actúa como el motor de integración y orquestación.

- Ingesta y Almacenamiento: Los datos ingresados se transforman y almacenan en formatos Parquet o Delta dentro de un lago de datos. El uso de Parquet permite consultas rápidas y eficientes gracias a su compresión por columnas, mientras que Delta añade capacidades de transacciones ACID, garantizando confiabilidad en el manejo de datos que se actualizan constantemente.

- Procesamiento en Databricks: Databricks se utiliza para procesar los datos mediante pipelines de transformación, integrando reglas de negocio y optimización de consultas. Los datos se gestionan a través de diferentes capas (Bronce, Silver, Gold) que corresponden a la calidad y transformación de los datos:

    - Bronce: Datos crudos.
    - Silver: Datos integrados y gobernados.
     Gold: Datos listos para el consumo analítico y modelos finales.
    
    Además, Databricks se apoya en Unity Catalog, que asegura la gobernanza y seguridad de  los datos, facilitando el control de acceso y linaje de los datos.

- Despliegue de Modelos con Databricks: La plataforma de MLflow integrada en Databricks permite gestionar el ciclo de vida completo de los modelos analíticos, desde su entrenamiento y experimentación hasta su validación y despliegue. Los modelos pueden ser expuestos mediante APIs REST para su consumo por aplicaciones externas, asegurando que las predicciones se realicen en tiempo real. Unity Catalog asegura que los datos utilizados en los modelos sean consistentes y estén debidamente gobernados, garantizando la seguridad y el linaje de los modelos desplegados.

- Consumo Final: Las aplicaciones de negocio y los sistemas de visualización como Power BI o Looker Studio se integran con los modelos para consumir las predicciones, permitiendo que los usuarios tomen decisiones basadas en datos actualizados y procesados eficientemente.

Esta arquitectura asegura una solución escalable y segura para el procesamiento, modelado y consumo de datos en tiempo real, permitiendo a las organizaciones optimizar sus flujos de trabajo analíticos y lograr un acceso confiable a modelos predictivos que impacten el negocio.

