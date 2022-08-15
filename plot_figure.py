import numpy as np
#!pip install dash

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import init_notebook_mode, iplot

def produce_loss_plot(y_pred, y_true):
  x = np.array(range(len(y_pred)))
  
  widths_true = np.array([1] * len(x))
  widths_pred = np.array([0.25] * len(x))
  x_extended = [(i,i) for i in x]
  y_extended = [(y_true[i], y_pred[i]) for i in x]
  differences = [round(y_extended[i][0]-y_extended[i][1], 2) for i in range(len(y_pred))]

  frames = []

  #####################
  ### Basic frames: ###
  data_0 = [go.Bar(),
            go.Bar(),
            go.Scatter(),
            go.Scatter(),
            go.Scatter(),
            go.Scatter(),
            ]

  data = [go.Bar(#x=[0, 1, 2, 3],
               x=np.cumsum(widths_true)-widths_true, 
               y=y_true,
               name="True values",
               opacity=0.95, 
               width=widths_true,
               marker_color="lightgreen",
               hoverinfo="text",
               hovertext=[f'True value: {i}' for i in y_true],
               ),
        go.Bar(x=np.cumsum(widths_true)-widths_true,  
               y=y_pred, 
               opacity = 0.65,
               name="Predicted values",
               width=widths_pred, 
               marker_color="blue", 
               hoverinfo="text",
               hovertext=[f'Predicted value: {i}' for i in y_pred],
               ),
         go.Scatter(),
         go.Scatter(),
         go.Scatter(),
         go.Scatter(),
        ]

  #######################################
  ###### Show differences between #######
  ######      y_pred, y_true      #######
  #######################################
  for i in range(0, len(y_pred)):
    data2 = [go.Bar(#x=[0, 1, 2, 3],
                  x=np.cumsum(widths_true)-widths_true, 
                  y=y_true,
                  name="True values",
                  opacity=0.95, 
                  width=widths_true,
                  marker_color="lightgreen",
                  hoverinfo="text",
                  hovertext=[f'True value: {i}' for i in y_true],
                  ),
            go.Bar(x=np.cumsum(widths_true)-widths_true,  
                  y=y_pred, 
                  opacity = 0.65,
                  name="Predicted values",
                  width=widths_pred, 
                  marker_color="blue", 
                  hoverinfo="text",
                  hovertext=[f'Predicted value: {i}' for i in y_pred],
                  )
            ]
    for j in range(i+1):
      data2.append(go.Scatter(x=x_extended[j], 
                        y=y_extended[j], 
                        #width=widths_diff,
                        mode='lines', 
                        marker_color="red", 
                        name=f"Difference = {round(y_extended[j][0]-y_extended[j][1], 2)}", 
                        opacity=1, 
                        hoverinfo="text",
                        hovertext=[f'{y_extended[j][0]-y_extended[j][1]}', f'{round(y_extended[j][0]-y_extended[j][1], 2)}'],
                        legendgroup='Differences',
                        ))
    for j in range(len(y_pred)-i+1):
      data2.append(go.Scatter())
    frames.append(go.Frame(data=data2))


  #####################################
  #### Show squared error bars:   #####
  #####################################
  data3 = [go.Bar(x=np.cumsum(widths_true)-widths_true, y=[0]*len(y_pred)), go.Bar(x=np.cumsum(widths_true)-widths_true, y=[0]*len(y_pred))]
  squared_points = []
  for i in range(0, len(differences)):
    squared_points.append([0, max(0.01, round(differences[i] * differences[i], 2))])
  
  for i in range(0, len(squared_points)):
    data3.append(go.Scatter(x=x_extended[i],
                          y = squared_points[i],
                          mode='lines', 
                          marker_color="darkred", 
                          name=f"Squared error = {squared_points[i][1]}", 
                          opacity=1, 
                          hoverinfo="text",
                          hovertext=[f'Squared error: {squared_points[i][1]}', f'Squared error: {squared_points[i][1]}'],
                          legendgroup='Squared error'
                          ))
  frames.append(go.Frame(data=data3))

  ###########################
  #### Show summed bars: ####
  ###########################

  consequtive_points = [[0, squared_points[i][1]]]
  for i in range(1, len(squared_points)):
    consequtive_points.append([consequtive_points[i-1][1], consequtive_points[i-1][1] + squared_points[i][1]] )

  print(f"Cons: {consequtive_points} \n seq:{squared_points}")
  data4 = [go.Bar(x=np.cumsum(widths_true)-widths_true, y=[0]*len(y_pred)), go.Bar(x=np.cumsum(widths_true)-widths_true, y=[0]*len(y_pred))]

  for i in range(0, len(squared_points)):
    data4.append(go.Scatter(x=consequtive_points[i],
                          y = [0,0],
                          mode='lines', 
                          marker_color="darkred", 
                          name=f"Squared error = {squared_points[i][1]}", 
                          opacity=1, 
                          hoverinfo="text",
                          hovertext=[f'Squared error: {squared_points[i][1]}', f'Squared error: {squared_points[i][1]}'],
                          legendgroup='Squared error',
                          ))
  frames.append(go.Frame(data=data4))

  ###########################
  #### Zoom in:
  ###########################

  frames.append(go.Frame(data=data4, layout=go.Layout(xaxis_range=[0,1], yaxis_range=[-0.5,0.5], xaxis = dict(
      tick0 = 0,
      dtick = 0.1))))

  ###########################
  ##### Create Layout: ######
  ###########################

  layout = go.Layout(
  plot_bgcolor='rgba(250,250,250,0.6)',
  barmode='overlay',
  hovermode="x unified",
  showlegend=True,
  xaxis = dict(
      tick0 = 0,
      dtick = 1,
      #autorange=True,
      #rangemode="normal"
  ),
  width=1000,
  transition = {'duration': 80000},
  updatemenus=[dict(type="buttons",
                        buttons=[dict(label="Play",
                                      method="animate",
                                      args=[None, {"frame": {"duration": 80000}}])])]
  )
  fig = dict(data=data, layout=layout, frames=frames)

  ranges = [[-0.5, 3.5],[-0.5, 3.5],[-0.5, 3.5],[0, 1]]
  #for f in fig.frames:
  #  f.layout.update(xaxis_range = ranges)

  return fig
  iplot(fig, show_link=False)

  