"""Agrega seccion de analisis de seleccion de caracteristicas al notebook RF."""
import nbformat

NB = "Selección_de_Características_con_Random_Forest.ipynb"
nb = nbformat.read(NB, as_version=4)

def md(src):
    return nbformat.v4.new_markdown_cell(src)

def code(src):
    return nbformat.v4.new_code_cell(src)

intro = """---

## **9. ¿CUÁNTAS PREGUNTAS SON REALMENTE NECESARIAS?**

La importancia individual no responde directamente la pregunta de \"¿con cuántas preguntas basta?\". Para responderla aplicamos tres estrategias complementarias:

1. **Importancia acumulada** — ordenamos las preguntas por importancia y vemos cuántas se necesitan para cubrir el 80%, 90% y 95% del total.
2. **Selección incremental Top-K** — re-entrenamos el modelo usando solo las K preguntas más importantes (K = 1, 2, …, 20) y medimos la precisión. Buscamos el codo donde añadir más preguntas ya no mejora.
3. **RFECV (Recursive Feature Elimination with Cross-Validation)** — sklearn elimina iterativamente la peor pregunta y valida con CV; encuentra de forma automática el subconjunto óptimo.

Adicionalmente usamos **permutation importance** como verificación robusta del ranking."""

cell_91 = """# Importancia acumulada de las preguntas (ya ordenadas en importancia_df)
importancia_df = importancia_df.reset_index(drop=True)
importancia_df['Importancia_acumulada'] = importancia_df['Importancia'].cumsum()

# Cuantas preguntas se necesitan para cubrir 80 / 90 / 95 % de la importancia total
def k_para_cubrir(pct):
    return int((importancia_df['Importancia_acumulada'] >= pct).idxmax()) + 1

k80 = k_para_cubrir(0.80)
k90 = k_para_cubrir(0.90)
k95 = k_para_cubrir(0.95)

print(f'Para cubrir el 80% de la importancia se necesitan: {k80} preguntas')
print(f'Para cubrir el 90% de la importancia se necesitan: {k90} preguntas')
print(f'Para cubrir el 95% de la importancia se necesitan: {k95} preguntas')

print('\\nRanking con importancia acumulada:')
print(importancia_df.to_string(index=False))

# Grafico de la importancia acumulada
plt.figure(figsize=(10, 5))
plt.plot(range(1, len(importancia_df) + 1),
         importancia_df['Importancia_acumulada'] * 100,
         marker='o', color='steelblue')
plt.axhline(80, color='orange', linestyle='--', label='80%')
plt.axhline(90, color='red', linestyle='--', label='90%')
plt.axhline(95, color='green', linestyle='--', label='95%')
plt.xlabel('Numero de preguntas (Top-K)')
plt.ylabel('Importancia acumulada (%)')
plt.title('Importancia acumulada por numero de preguntas')
plt.xticks(range(1, len(importancia_df) + 1))
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()
"""

cell_92 = """# Re-entrenamos el modelo usando solo las K preguntas mas importantes
# y medimos la precision sobre el mismo X_test/y_test.

ranking = importancia_df['Característica'].tolist()
resultados_k = []

for k in range(1, len(ranking) + 1):
    top_k = ranking[:k]
    modelo_k = RandomForestClassifier(n_estimators=100, random_state=30, n_jobs=-1)
    modelo_k.fit(X_train[top_k], y_train)
    pred_k = modelo_k.predict(X_test[top_k])
    acc_k = accuracy_score(y_test, pred_k)
    resultados_k.append({'K': k, 'preguntas': top_k, 'precision': acc_k})
    print(f'K={k:2d}  precision={acc_k:.4f}  ({top_k[-1]} agregada)')

resultados_df = pd.DataFrame(resultados_k)

# Grafico K vs precision
plt.figure(figsize=(10, 5))
plt.plot(resultados_df['K'], resultados_df['precision'], marker='o', color='darkgreen')
plt.axhline(precision, color='red', linestyle='--',
            label=f'Precision con las 20 preguntas: {precision:.4f}')
plt.xlabel('Numero de preguntas usadas (Top-K)')
plt.ylabel('Precision en test')
plt.title('Precision del modelo segun numero de preguntas')
plt.xticks(range(1, len(ranking) + 1))
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# Identificar el K minimo que alcanza al menos el 99% de la precision total
umbral = 0.99 * precision
k_minimo = int(resultados_df.loc[resultados_df['precision'] >= umbral, 'K'].min())
print(f'\\nK minimo que alcanza >= 99% de la precision total ({precision:.4f}): {k_minimo}')
print(f'Preguntas seleccionadas: {ranking[:k_minimo]}')
"""

cell_93 = """from sklearn.feature_selection import RFECV
from sklearn.model_selection import StratifiedKFold

# Para que RFECV no tarde demasiado con 226k filas, usamos una sub-muestra estratificada
muestra_n = min(20000, len(X_train))
idx = X_train.sample(n=muestra_n, random_state=30).index
X_sub, y_sub = X_train.loc[idx], y_train.loc[idx]

estimator = RandomForestClassifier(n_estimators=100, random_state=30, n_jobs=-1)
rfecv = RFECV(
    estimator=estimator,
    step=1,
    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=30),
    scoring='accuracy',
    min_features_to_select=1,
    n_jobs=-1,
)
rfecv.fit(X_sub, y_sub)

print(f'Numero optimo de preguntas segun RFECV: {rfecv.n_features_}')
seleccionadas = X.columns[rfecv.support_].tolist()
print(f'Preguntas seleccionadas: {seleccionadas}')

# Curva CV
scores = rfecv.cv_results_['mean_test_score']
plt.figure(figsize=(10, 5))
plt.plot(range(1, len(scores) + 1), scores, marker='o', color='purple')
plt.xlabel('Numero de preguntas usadas')
plt.ylabel('Precision media (CV 5-fold)')
plt.title('RFECV: precision por tamano del subconjunto')
plt.xticks(range(1, len(scores) + 1))
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
"""

cell_94 = """from sklearn.inspection import permutation_importance

# Permutation importance se calcula sobre test con el modelo ya entrenado.
# Para acelerar, usamos una sub-muestra del test.
test_idx = X_test.sample(n=min(10000, len(X_test)), random_state=30).index
result = permutation_importance(
    rf_model, X_test.loc[test_idx], y_test.loc[test_idx],
    n_repeats=5, random_state=30, n_jobs=-1, scoring='accuracy'
)

perm_df = pd.DataFrame({
    'Característica': X.columns,
    'Importancia_perm_media': result.importances_mean,
    'Importancia_perm_std':   result.importances_std,
}).sort_values('Importancia_perm_media', ascending=False).reset_index(drop=True)

print('Permutation importance:')
print(perm_df.to_string(index=False))

# Comparar el ranking de feature_importances_ vs permutation
comparativa = pd.merge(
    importancia_df[['Característica', 'Importancia']].rename(columns={'Importancia': 'Imp_Gini'}),
    perm_df[['Característica', 'Importancia_perm_media']],
    on='Característica'
)
comparativa['Rank_Gini'] = comparativa['Imp_Gini'].rank(ascending=False).astype(int)
comparativa['Rank_Perm'] = comparativa['Importancia_perm_media'].rank(ascending=False).astype(int)
print('\\nComparativa de rankings:')
print(comparativa.sort_values('Rank_Gini').to_string(index=False))
"""

cell_95 = """print('=' * 65)
print(' RESUMEN: ¿CUANTAS PREGUNTAS SON REALMENTE NECESARIAS?')
print('=' * 65)

print(f'\\nPrecision usando las 20 preguntas:           {precision:.4f}')

print('\\n[Estrategia 1] Importancia acumulada')
print(f'  - 80 % de la importancia: {k80} preguntas')
print(f'  - 90 % de la importancia: {k90} preguntas')
print(f'  - 95 % de la importancia: {k95} preguntas')

print('\\n[Estrategia 2] Top-K incremental (umbral: >= 99% de la precision total)')
print(f'  - Minimo K necesario: {k_minimo} preguntas')
print(f'  - Preguntas elegidas: {ranking[:k_minimo]}')

print('\\n[Estrategia 3] RFECV (validacion cruzada 5-fold)')
print(f'  - K optimo: {rfecv.n_features_} preguntas')
print(f'  - Preguntas elegidas: {seleccionadas}')

print('\\n[Recomendacion]')
recomendado = sorted(set(ranking[:k_minimo]) | set(seleccionadas))
print(f'  - Conjunto recomendado (union Top-K + RFECV): {len(recomendado)} preguntas')
print(f'    {recomendado}')
interseccion = sorted(set(ranking[:k_minimo]) & set(seleccionadas))
print(f'  - Conjunto minimo defendible (interseccion): {len(interseccion)} preguntas')
print(f'    {interseccion}')
"""

cierre = """### Cómo interpretar los tres resultados

- **Importancia acumulada** dice cuántas preguntas concentran la \"señal\", pero no garantiza que el modelo prediga igual de bien con menos.
- **Top-K incremental** mide directamente el impacto en precisión y suele ser el más práctico para decidir un corte: el K mínimo que mantiene ≥ 99 % de la precisión total es el \"número defendible\" de preguntas.
- **RFECV** valida con cross-validation y resiste mejor a sobreajuste; suele coincidir con el codo del Top-K.

**Regla general:** si las tres estrategias coinciden alrededor de un mismo K (típicamente entre 8 y 14 preguntas en encuestas de 20 ítems), ese K es un buen candidato para una versión reducida de la encuesta. Si difieren, conviene quedarse con la **unión** de los conjuntos para no perder señal o con la **intersección** si se quiere maximizar la reducción."""

nuevas = [
    md(intro),
    md("### 9.1 Importancia acumulada"),
    code(cell_91),
    md("### 9.2 Selección incremental Top-K (precisión vs. número de preguntas)"),
    code(cell_92),
    md("### 9.3 RFECV — búsqueda automática del K óptimo"),
    code(cell_93),
    md("### 9.4 Validación con Permutation Importance (más robusto que feature_importances_)"),
    code(cell_94),
    md("### 9.5 Conclusión final"),
    code(cell_95),
    md(cierre),
]

for c in nuevas:
    nb.cells.append(c)

nbformat.write(nb, NB)
print(f"Notebook actualizado. Total celdas: {len(nb.cells)}")
