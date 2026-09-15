"""
ml_dl_masterclass_demo.py
End-to-end demo suite for the 08/25/2026 ML & DL masterclass.
Sections: (1) Regression Lab  (2) Classical Classification Benchmarks
          (3) Tree Ensembles & Analytics  (4) Neural Networks & PyTorch Attention

Run: python ml_dl_masterclass_demo.py
Requires: numpy, scikit-learn, xgboost, torch
"""

import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import torch
import torch.nn as nn

RNG = np.random.RandomState(42)


def banner(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# =============================================================================
# SECTION 1: REGRESSION LAB
# =============================================================================
def section1_regression_lab():
    """OLS via the Normal Equation, then OLS vs. Ridge vs. Lasso on collinear data."""
    banner("SECTION 1: REGRESSION LAB")

    # Collinear synthetic data: x2 and x3 are near-duplicates of x1
    n = 200
    x1 = RNG.normal(0, 1, n)
    x2 = x1 + RNG.normal(0, 0.01, n)   # near-collinear with x1
    x3 = x1 + RNG.normal(0, 0.01, n)   # near-collinear with x1
    x4 = RNG.normal(0, 1, n)           # independent, irrelevant feature
    X = np.column_stack([x1, x2, x3, x4])
    true_beta = np.array([3.0, 0.0, 0.0, 0.0])
    y = X @ true_beta + 5 + RNG.normal(0, 0.5, n)

    # --- Analytic OLS via Normal Equation: theta = (X^T X)^-1 X^T y ---
    X_design = np.column_stack([np.ones(n), X])  # bias column
    theta = np.linalg.pinv(X_design.T @ X_design) @ X_design.T @ y
    print("Normal Equation solution [bias, b1, b2, b3, b4]:")
    print(np.round(theta, 3))

    # --- sklearn OLS / Ridge / Lasso comparison ---
    ols = LinearRegression().fit(X, y)
    ridge = Ridge(alpha=5.0).fit(X, y)
    lasso = Lasso(alpha=0.5).fit(X, y)

    print("\nCoefficient comparison on collinear features [b1, b2, b3, b4]:")
    print(f"  OLS   : {np.round(ols.coef_, 3)}   (unstable — splits weight across x1,x2,x3)")
    print(f"  Ridge : {np.round(ridge.coef_, 3)}   (shrinks all three collinear weights together)")
    print(f"  Lasso : {np.round(lasso.coef_, 3)}   (zeroes out redundant/irrelevant features)")


# =============================================================================
# SECTION 2: CLASSICAL CLASSIFICATION BENCHMARKS (2D SYNTHETIC DATA)
# =============================================================================
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def logistic_regression_scratch(X, y, lr=0.1, epochs=2000):
    """Binary logistic regression fit with plain NumPy gradient descent on BCE loss."""
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(epochs):
        z = X @ w + b
        y_hat = sigmoid(z)
        grad_w = X.T @ (y_hat - y) / n
        grad_b = np.mean(y_hat - y)
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b


def section2_classical_classification():
    """Logistic regression from scratch + sklearn kNN/SVM/Tree/Forest on the same 2D dataset."""
    banner("SECTION 2: CLASSICAL CLASSIFICATION BENCHMARKS")

    X, y = make_classification(n_samples=400, n_features=2, n_redundant=0,
                                n_clusters_per_class=1, class_sep=1.5, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    scaler = StandardScaler().fit(X_train)
    X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

    # --- from-scratch logistic regression ---
    w, b = logistic_regression_scratch(X_train_s, y_train)
    y_pred_scratch = (sigmoid(X_test_s @ w + b) >= 0.5).astype(int)

    results = {
        "Logistic Regression (scratch)": y_pred_scratch,
        "k-NN (k=5)": KNeighborsClassifier(n_neighbors=5).fit(X_train_s, y_train).predict(X_test_s),
        "SVM (linear)": SVC(kernel="linear").fit(X_train_s, y_train).predict(X_test_s),
        "SVM (RBF)": SVC(kernel="rbf").fit(X_train_s, y_train).predict(X_test_s),
        "Decision Tree": DecisionTreeClassifier(max_depth=4, random_state=42).fit(X_train_s, y_train).predict(X_test_s),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42).fit(X_train_s, y_train).predict(X_test_s),
    }

    print(f"{'Model':<32}{'Accuracy':<12}{'F1-Score':<10}")
    print("-" * 54)
    for name, y_pred in results.items():
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        print(f"{name:<32}{acc:<12.3f}{f1:<10.3f}")

    return X_train_s, X_test_s, y_train, y_test


# =============================================================================
# SECTION 3: TREE ENSEMBLES & ANALYTICS
# =============================================================================
def section3_ensembles_and_analytics(X_train, X_test, y_train, y_test):
    """XGBoost feature importance + Isolation Forest anomaly scoring."""
    banner("SECTION 3: TREE ENSEMBLES & ANALYTICS")

    xgb_clf = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1,
                                 eval_metric="logloss", random_state=42)
    xgb_clf.fit(X_train, y_train)
    y_pred = xgb_clf.predict(X_test)
    print(f"XGBoost accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print(f"XGBoost feature importances: {np.round(xgb_clf.feature_importances_, 3)}")

    # Isolation Forest: inject synthetic outliers into the training features
    outliers = RNG.uniform(low=-6, high=6, size=(15, X_train.shape[1]))
    data_with_outliers = np.vstack([X_train, outliers])
    iso = IsolationForest(contamination=0.05, random_state=42).fit(data_with_outliers)
    scores = iso.decision_function(data_with_outliers)
    flags = iso.predict(data_with_outliers)  # -1 = anomaly, 1 = normal
    n_flagged = int(np.sum(flags == -1))
    print(f"\nIsolation Forest: flagged {n_flagged}/{len(data_with_outliers)} points as anomalies")
    print(f"Lowest 5 anomaly scores (most anomalous): {np.round(np.sort(scores)[:5], 3)}")


# =============================================================================
# SECTION 4: NEURAL NETWORKS & PYTORCH ATTENTION
# =============================================================================
class MLP(nn.Module):
    """Two-hidden-layer perceptron with ReLU activations."""

    def __init__(self, in_dim, hidden=16, out_dim=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.net(x)


def train_mlp(X_train, y_train, X_test, y_test, epochs=200):
    Xtr = torch.tensor(X_train, dtype=torch.float32)
    ytr = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    Xte = torch.tensor(X_test, dtype=torch.float32)
    yte = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

    model = MLP(in_dim=X_train.shape[1])
    loss_fn = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.05)

    for epoch in range(epochs):
        optimizer.zero_grad()
        logits = model(Xtr)
        loss = loss_fn(logits, ytr)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 50 == 0:
            print(f"  epoch {epoch + 1:>4} | loss {loss.item():.4f}")

    with torch.no_grad():
        preds = (torch.sigmoid(model(Xte)) >= 0.5).float()
        acc = (preds == yte).float().mean().item()
    print(f"MLP test accuracy: {acc:.3f}")


def scaled_dot_product_attention(Q, K, V):
    """softmax(QK^T / sqrt(d_k)) V ; Q,K,V shaped (batch, seq_len, d_k)."""
    d_k = Q.shape[-1]
    scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)
    weights = torch.softmax(scores, dim=-1)
    return torch.matmul(weights, V), weights


def section4_neural_nets_and_attention(X_train, X_test, y_train, y_test):
    banner("SECTION 4: NEURAL NETWORKS & PYTORCH ATTENTION")

    print("Training MLP (explicit loss.backward() + optimizer.step()):")
    train_mlp(X_train, y_train, X_test, y_test)

    print("\nScaled Dot-Product Attention demo:")
    batch_size, seq_len, d_k = 2, 5, 8
    torch.manual_seed(42)
    Q = torch.randn(batch_size, seq_len, d_k)
    K = torch.randn(batch_size, seq_len, d_k)
    V = torch.randn(batch_size, seq_len, d_k)
    output, attn_weights = scaled_dot_product_attention(Q, K, V)
    print(f"  Q/K/V shape : {tuple(Q.shape)}")
    print(f"  output shape: {tuple(output.shape)}")
    print(f"  attention weights sum to 1 per row: {torch.allclose(attn_weights.sum(-1), torch.ones(batch_size, seq_len))}")


if __name__ == "__main__":
    section1_regression_lab()
    X_train, X_test, y_train, y_test = section2_classical_classification()
    section3_ensembles_and_analytics(X_train, X_test, y_train, y_test)
    section4_neural_nets_and_attention(X_train, X_test, y_train, y_test)
    banner("MASTERCLASS DEMO COMPLETE")
