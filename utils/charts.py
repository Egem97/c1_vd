import plotly.express as px
import pandas as pd

def plot_bar(df, x, y, title, text=None, orientation='h', color=None, barmode=None, xaxis_title=None, yaxis_title=None, font_size=16):
    fig = px.bar(
        df, x=x, y=y, text=text or y, orientation=orientation, title=title, color=color, barmode=barmode
    )
    fig.update_traces(textfont_size=font_size, textangle=0, textposition="outside", cliponaxis=False)
    if xaxis_title:
        fig.update_layout(xaxis=dict(title=dict(text=xaxis_title)))
    if yaxis_title:
        fig.update_layout(yaxis=dict(title=dict(text=yaxis_title)))
    fig.update_layout(font=dict(size=font_size), margin=dict(t=30, b=20))
    return fig