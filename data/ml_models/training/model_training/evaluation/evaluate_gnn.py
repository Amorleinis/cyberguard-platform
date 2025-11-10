"""
Evaluate GNN model predictions using standard metrics (accuracy, precision, recall, F1).
"""
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Example: Load predictions and ground truth
preds = pd.read_csv('predictions.csv')  # columns: id, pred, true

acc = accuracy_score(preds['true'], preds['pred'])
prec = precision_score(preds['true'], preds['pred'], average='weighted')
rec = recall_score(preds['true'], preds['pred'], average='weighted')
f1 = f1_score(preds['true'], preds['pred'], average='weighted')

print(f'Accuracy: {acc:.3f}')
print(f'Precision: {prec:.3f}')
print(f'Recall: {rec:.3f}')
print(f'F1 Score: {f1:.3f}')
