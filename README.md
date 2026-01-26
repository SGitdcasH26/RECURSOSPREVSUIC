# 🧭 Recursos de Prevención y Posvención del Suicidio en Andalucía

![Estado](https://img.shields.io/badge/Estado-Finalizado-success)
![Lenguaje](https://img.shields.io/badge/Python-3.9%2B-blue)
![Framework](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![Licencia](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)

**Herramienta digital de soporte a la decisión para la localización rápida de recursos de salud mental y prevención del suicidio.**

---

## 📋 Descripción del Proyecto

Esta aplicación web ("Web App") ha sido desarrollada para centralizar, filtrar y facilitar el acceso a los recursos disponibles en Andalucía para el abordaje de la conducta suicida. 

Su objetivo principal es reducir el tiempo de búsqueda de ayuda en situaciones de crisis, sirviendo como herramienta de apoyo tanto para **profesionales sanitarios (061, Urgencias, Atención Primaria)** como para pacientes, familiares y supervivientes.

### 🎯 Funcionalidades Clave
* **Filtrado Inteligente por Perfil:** El algoritmo adapta los resultados según el usuario (Ideación suicida, Familiar/Entorno, Profesional Sanitario, Superviviente en duelo).
* **Geolocalización:** Búsqueda por Provincia y Localidad (Andalucía).
* **Priorización Clínica:** Los recursos de emergencia (112, 061, 024) se priorizan automáticamente ante perfiles de riesgo inminente.
* **Interfaz Adaptativa:** Diseño *responsive* optimizado para uso en móviles y tablets.



## 🛠️ Tecnologías Utilizadas

El proyecto está construido íntegramente en **Python**, utilizando las siguientes librerías:

* **[Streamlit](https://streamlit.io/):** Para la creación de la interfaz web interactiva y el despliegue rápido.
* **[Pandas](https://pandas.pydata.org/):** Para la gestión, limpieza y filtrado de la base de datos (`recursos.csv`).

## 🚀 Instalación y Uso Local

Si deseas ejecutar esta herramienta en tu ordenador local:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/NOMBRE_DEL_REPO.git](https://github.com/TU_USUARIO/NOMBRE_DEL_REPO.git)
    ```
2.  **Instalar dependencias:**
    Asegúrate de tener Python instalado y ejecuta:
    ```bash
    pip install streamlit pandas
    ```
3.  **Ejecutar la aplicación:**
    ```bash
    streamlit run app.py
    ```

## 📂 Estructura de Datos

La aplicación se alimenta de un archivo dinámico `recursos.csv` que actúa como base de datos. Este archivo permite la actualización de teléfonos, enlaces y direcciones sin necesidad de modificar el código fuente de la aplicación.

## 👩‍⚕️ Autoría y Propiedad Intelectual

**Autora:** Susana de Castro García  
*Enfermera de Emergencias Prehospitalarias (Jaén, Andalucía)* *Fecha de publicación: Enero 2026*

### Registro y Licencia
Este proyecto cuenta con un registro de propiedad intelectual y se distribuye bajo una licencia que protege la autoría y prohíbe el uso comercial.

* 🛡️ **Registro Safe Creative:** Inscripción nº **2301254360025**
* ⚖️ **Licencia:** [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es)

> **Usted es libre de:** Compartir y adaptar el material.  
> **Bajo las condiciones:** Debe reconocer la autoría, no puede usar el material con fines comerciales y debe compartir bajo la misma licencia.

---
*Nota de descargo: Esta herramienta actúa como un directorio facilitador. Los derechos de propiedad intelectual de los recursos externos enlazados (asociaciones, organismos oficiales) pertenecen a sus respectivos autores.*
