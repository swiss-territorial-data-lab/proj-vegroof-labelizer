import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, fbeta_score, recall_score, precision_score
import warnings


def show_confusion_matrix(y_pred, y_true, target_src,class_labels, title="", do_save=True, do_show=False):
    """
    Plot confusion matrix and associated metrics.

    Args:
    - y_pred (list): List of predicted labels.
    - y_true (list): List of true labels.
    - target_src (str): File path where the plot will be saved.
    - class_labels (list): List of class names corresponding to the labels.
    - title (str, optional): Title of the plot. Default is an empty string.
    - do_save (bool, optional): If True, save the plot. Default is True.
    - do_show (bool, optional): If True, display the plot. Default is False.

    Returns:
    - None
    """
    warnings.filterwarnings('ignore')
    n_classes = len(class_labels)

    # confusion matrix
    conf_mat = np.round(confusion_matrix(y_true, y_pred, labels=range(0, n_classes), normalize='true'),2)
    df_conf_mat = pd.DataFrame(conf_mat, index=class_labels, columns=class_labels)

    # metrics
    recall = recall_score(y_true, y_pred, labels=range(0, n_classes), average=None)
    precision = precision_score(y_true, y_pred, labels=range(0, n_classes), average=None)
    f1 = f1_score(y_true, y_pred, labels=range(0, n_classes), average=None)
    f2 = fbeta_score(y_true, y_pred, labels=range(0, n_classes), average=None, beta=2)
    f05 = fbeta_score(y_true, y_pred, labels=range(0, n_classes), average=None, beta=0.5)
    acc = confusion_matrix(y_true, y_pred, labels=range(0, n_classes)).diagonal() / confusion_matrix(y_true, y_pred, labels=range(0, n_classes)).sum(axis=1)


    df_metrics = pd.DataFrame(index=class_labels)
    df_metrics['OA'] = acc
    df_metrics['Recall'] = recall
    df_metrics['F2'] = f2
    df_metrics['F1'] = f1
    df_metrics['F05'] = f05
    df_metrics['Precision'] = precision
    df_metrics.loc["Global"] = [
        accuracy_score(y_true, y_pred),
        recall_score(y_true, y_pred, labels=range(0, n_classes), average="macro"),
        fbeta_score(y_true, y_pred, labels=range(0, n_classes), average="macro", beta=2),
        f1_score(y_true, y_pred, labels=range(0, n_classes), average="macro"),
        fbeta_score(y_true, y_pred, labels=range(0, n_classes), average="macro", beta=0.5),
        precision_score(y_true, y_pred, labels=range(0, n_classes), average="macro"),
        ]

    # plotting
    fig,axs = plt.subplots(1,2,figsize=(10,6))
    subfig_confmat = sns.heatmap(df_conf_mat, annot=True, cmap=sns.color_palette("Blues", as_cmap=True), cbar=False, ax=axs[0])
    subfig_metrics = sns.heatmap(df_metrics, annot=True, cmap=sns.color_palette("Blues", as_cmap=True), cbar_kws = dict(location="left"), ax=axs[1])
    subfig_metrics.tick_params(right=True, labelright=True, labelleft=False)
    plt.yticks(rotation='horizontal')
    axs[0].set_ylabel('True labels')
    axs[0].set_xlabel('Predicted labels')
    axs[0].set_title('Confusion matrix')
    axs[1].set_title('Metrics')
    axs[1].set_xlabel('Indexes')
    fig.suptitle(title)
    plt.tight_layout()

    if do_save:
        plt.savefig(target_src)

    if do_show:
        plt.show()

    plt.close()


