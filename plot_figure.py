class PlotLossLesson:
  empty_bar = go.Bar(visible=True)
  zero_bar = go.Bar(y=[0])

  empty_scatter = go.Scatter(visible=True)
  zero_scatter = go.Scatter(x=[0], y=[0])


  def __init__(self, vals_true, vals_pred):
    ## define basic properties:
    self.vals_true = vals_true
    self.vals_pred = vals_pred
    self.base_x=np.array(range(len(vals_true)))
    self.differences = [self.vals_true[i]-self.vals_pred[i] for i in self.base_x]
    self.traces = np.array(range(2 + len(self.base_x) + 1))

    # prepare plot components: bars and scatters:
    self.true_bars=self.get_bars_data(vals_true, true_or_pred="true")
    self.pred_bars=self.get_bars_data(vals_pred, true_or_pred="pred")
    self.error_scatter=self.get_difference_bars()

    # Prepare template for a basic plot:
    self.basic_plot_data = [self.empty_bar, self.empty_bar]
    for i in range(len(self.vals_true)):
      self.basic_plot_data.append(self.empty_scatter)
    self.basic_plot_data.append(self.empty_bar)

    # prepare figure with two subplots and all necessary traces:
    self.figure = self.create_plot_template()

    self.frames=None

  def create_plot_template(self):
    fig = make_subplots(rows=1, 
                    cols=2,
                    shared_yaxes="rows",
                    column_widths=[0.7, 0.3],
                    column_titles=["True & predicted values", "Error"]
                     )

    fig.add_trace(go.Bar(), row=1, col=1) # trace 0
    fig.add_trace(go.Bar(), row=1, col=1) # trace 1

    for i in self.base_x:
      fig.add_trace(go.Scatter(), row=1, col=1) # trace n

    fig.add_trace(go.Bar(), row=1, col=2) # trace [-1]

    return fig


  def prepare_frames(self, frames_data:list):
    frames = [go.Frame(data=data, traces=self.traces) for data in frames_data]
    return(frames)

  def get_bars_data(self, vals, true_or_pred="true"):
    '''
    Function that return go.Bar() object with n bars (n=len(vals)), with properly defined spacing.
    Suitable for both predicted and true values.
    '''
    color="blue"
    if true_or_pred=="true":
      widths = np.array([1] * len(self.base_x))
      name="True value"
      color="lightgreen"
    elif true_or_pred=="pred":
      widths = np.array([0.25] * len(self.base_x))
      name="Predicted value"
      color="blue"
    else:
      return 1
    bars = go.Bar(x=self.base_x, 
                y=vals,
                name=name+"s",
                opacity=0.95, 
                width=widths,
                marker_color=color,
                hoverinfo="text",
                hovertext=[f'{name}: {i}' for i in vals])

    return bars

  def get_difference_bars(self):
    '''
    Function returns a list of go.Scatter objects (len(list)==len(vals_true)==len(vals_pred))
    The Scatter is used as it's easier to position.
    '''

    # extend values: plots are vertical lines, so all need two x and two y coords:
    x_extended = [(i,i) for i in self.base_x]
    y_extended = [(self.vals_true[i], self.vals_pred[i]) for i in self.base_x]

    plots = []

    for i in range(len(self.vals_true)):
      plots.append(go.Scatter(x=x_extended[i], 
                        y=y_extended[i], 
                        mode='lines', 
                        marker_color="red", 
                        name=f"Difference = {round(self.differences[i], 2)}", 
                        opacity=1, 
                        hoverinfo="text",
                        hovertext=[f'Difference: {round(self.differences[i], 2)}', f'Difference: {round(self.differences[i], 2)}'],
                        legendgroup='Differences',
                        ))
    return(plots)

  def true_and_pred_difference_subplot_1_frames_data(self)->None:
    '''
    Prepare frames for first subplots (true values, predicted values, and errors). In total 3 frames.
    '''
    if (self.true_bars==None) or (self.pred_bars==None) or (self.error_scatter==None):
      return 1
    else:

      # frame 1 (true vals):
      data1 = self.basic_plot_data.copy()
      data1[0] = self.true_bars

      # frame 2 (+= predicted_vals):
      data2 = data1.copy()
      data2[1] = self.pred_bars

      # frame 3 (+= errors):
      data3=data2.copy()
      data3[2:-1] = self.error_scatter

      datas =[self.basic_plot_data, data1, data2, data3]
      return(datas)


'''
================================================================================
'''

class PlotLessonMSE(PlotLossLesson):
  def __init__(self, x, y):
    super().__init__(x, y) 
    # 3 frames for first plot visualisation, 1 frame for squared error visualisation, n frames for error summed
    n = len(self.vals_true)
    self.no_frames = 3 + 1 + n
 
    # Define 4 first sets of data (empty, true values, predicted values, and errors):
    true_pred_diff_frames_data = self.true_and_pred_difference_subplot_1_frames_data()
    self.the_last_frame = true_pred_diff_frames_data[-1].copy()
    self.data_for_frames = true_pred_diff_frames_data.copy()

    # calculate errors
    self.errors_squared = self.error_squared()

    # Define further frames:
    squared_error_frames_data = self.squared_error_frames_data()
    self.data_for_frames.append(squared_error_frames_data)

    summed_error_frames_data= self.summed_error_frames_data(squared_error_frames_data, self.the_last_frame)
    self.data_for_frames += summed_error_frames_data
    self.data_for_frames.append(self.mean_error_frames_data(summed_error_frames_data[-1]))
    
    # prepare frames on the basis of data:
    self.frames = self.prepare_frames(self.data_for_frames)
    self.figure.frames=self.frames
    self.update_figure_layout()
    

  def update_figure_layout(self)->None:
    xxs_range = [-0.6, max(self.base_x)+0.5]
    self.figure.update_xaxes(range=xxs_range, row=1, col=1)
    self.figure.update_xaxes(range=[-0.5, 0.5], row=1, col=2)
    self.figure.update_yaxes(range=[-0.1, 1.1])
    self.figure.update_layout(title_text="Mean Squared Error",
                      barmode="overlay",
                      width=1250,
                      updatemenus=[dict(type="buttons",
                            buttons=[dict(label="Play",
                                          method="animate",
                                          args=[None, {"frame": {"duration": 2000}}])])],
                      margin={'r':250, 'l': 50},
    )


  def show_figure(self)->None:
    self.figure.show()


  def error_squared(self):
    '''
    Return a list of squared errors based on previously computed errors.
    '''
    return [self.differences[i] * self.differences[i] for i in self.base_x]

  def squared_error_frames_data(self)->list:
    '''
    1st FRAME
     Basic alignement of elements is: bar, bar, n x scatter, bar. Here i modify scatters to show squared error only,
     Without the bars indicating predictions and true values

     Return a list of objects that together constitute a frame.

    '''

    #data = self.basic_plot_data.copy()  # originally contains [bar(),bar(), scatter()*n and bar()]. The last bar is empty at this frame, so there is no need to override it.

    # make bars disappear:
    data = [self.zero_bar, self.zero_bar]

    # make Scatters show squared error:
    x_extended = [(i,i) for i in self.base_x]
    y_extended = [(self.vals_true[i], self.vals_pred[i]) for i in self.base_x]

    for i in self.base_x:
      data.append(go.Scatter(x=x_extended[i], 
                        y=[0, self.errors_squared[i]], 
                        mode='lines', 
                        marker_color="red", 
                        name=f"Difference squared = {round(self.errors_squared[i], 2)}", 
                        opacity=1,
                        hoverinfo="text",
                        hovertext=[f'{round(self.errors_squared[i], 2)}', f'{round(self.errors_squared[i], 2)}'],
                        legendgroup='Differences squared',
                        ))
      
    data.append(self.zero_bar)
    return data


  def summed_error_frames_data(self, squared_error_frames_data, true_pred_diff_frames_data)->list:
    '''
    2nd FRAME
    Build n frames that will make the separate error bars disappear, and instead show summed error

    Arguments:
    squared_error_data:list -> the data for frame in which error bars are defined;
    true_pred_diff_data:list - > the data for frame that will be visible at the very end, when the error bars are summed.

    '''
    data_frames = []
    base_data = squared_error_frames_data.copy()
    for i in self.base_x[:-1]:
      base_data = base_data.copy()
      base_data[i+2] = self.zero_scatter
      error_summed = sum(self.errors_squared[0:i+1])
      base_data[-1] = go.Bar(x=[0], 
                            y=[error_summed],
                              name="Error summed",
                              opacity=0.95, 
                              width=[0.5],
                              marker_color="lightcoral",
                              hoverinfo="text",
                              hovertext=[[f'Squared error summed: {error_summed}']])
      
      data_frames.append(base_data)

    base_data=true_pred_diff_frames_data.copy()
    error_summed = sum(self.errors_squared)
    base_data[-1] = go.Bar(x=[0], 
                          y=[error_summed],
                          name="Squared Error summed",
                          opacity=0.95, 
                          width=[0.5],
                          marker_color="lightcoral",
                          hoverinfo="text",
                          hovertext=[[f'Squared error summed: {error_summed}']])


    data_frames.append(base_data)

    return data_frames


  def mean_error_frames_data(self, summed_error_data)->list:
    '''
    Build a frame representing mean error
    (LAST frame)
    '''

    data = summed_error_data.copy()
    mean_error = sum(self.errors_squared)/len(self.vals_true)

    data[-1] = go.Bar(x=[0], 
                      y=[mean_error],
                      name="Mean Squared Error",
                      opacity=0.95, 
                      width=[0.45],
                      marker_color="coral",
                      hoverinfo="text",
                      hovertext=[[f'Mean Squared Error: {round(mean_error, 2)}']])

    return data