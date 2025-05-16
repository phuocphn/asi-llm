import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Define confusion matrices for each hierarchy level

# HL1
hl1_labels = ["MosfetDiode", "load_cap", "compensation_cap"]
hl1_matrix = np.array([[1952, 0, 0], [0, 215, 0], [0, 0, 405]])

# HL2
hl2_labels = ["CM", "Inverter", "DiffPair"]
hl2_matrix = np.array(
    [[4241, 451, 14], [1120, 687, 51], [10, 20, 260]]  # CM  # Inverter  # DiffPair
)

# HL3
hl3_labels = [
    "firstStage",
    "secondStage",
    "thirdStage",
    "loadPart",
    "biasPart",
    "feedBack",
]
hl3_matrix = np.array(
    [
        [600, 0, 0, 0, 20, 0],  # firstStage
        [0, 109, 0, 0, 659, 0],  # secondStage
        [0, 55, 0, 0, 100, 0],  # thirdStage
        [0, 35, 0, 763, 592, 0],  # loadPart
        [0, 181, 0, 0, 3749, 0],  # biasPart
        [0, 0, 0, 0, 340, 0],  # feedBack
    ]
)

# Plotting
fig, axs = plt.subplots(1, 3, figsize=(18, 5))
sns.set(style="whitegrid")

# HL1 Plot
sns.heatmap(
    hl1_matrix,
    annot=True,
    fmt="d",
    xticklabels=hl1_labels,
    yticklabels=hl1_labels,
    ax=axs[0],
    cmap="Blues",
)
axs[0].set_title("Confusion Matrix - HL1")
axs[0].set_xlabel("Predicted")
axs[0].set_ylabel("Actual")

# HL2 Plot
sns.heatmap(
    hl2_matrix,
    annot=True,
    fmt="d",
    xticklabels=hl2_labels,
    yticklabels=hl2_labels,
    ax=axs[1],
    cmap="Greens",
)
axs[1].set_title("Confusion Matrix - HL2")
axs[1].set_xlabel("Predicted")
axs[1].set_ylabel("Actual")

# HL3 Plot
sns.heatmap(
    hl3_matrix,
    annot=True,
    fmt="d",
    xticklabels=hl3_labels,
    yticklabels=hl3_labels,
    ax=axs[2],
    cmap="Oranges",
)
axs[2].set_title("Confusion Matrix - HL3")
axs[2].set_xlabel("Predicted")
axs[2].set_ylabel("Actual")

plt.tight_layout()

plt.savefig("confusion_matrices.png", dpi=300)
plt.show()
