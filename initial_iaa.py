@loginrequired
def iaa(request):

    batchname = basefile.objects.filter(Q(batch_name__isnull=False) & ~Q(batch_name='')).values('batch_name').distinct()

    if request.method == 'POST':

        try:
            
            fromdate = request.POST.get('fromdate')
            todate = request.POST.get('todate')
            batchname_filter = request.POST.get('batchname')

            from datetime import datetime, timedelta

            fromdates = datetime.strptime(fromdate, '%Y-%m-%d')
            todates = datetime.strptime(todate, '%Y-%m-%d')

            date_difference = (todates - fromdates).days

            list_of_dates = [fromdates + timedelta(days=i) for i in range(date_difference + 1)]

            formatted_dates = [date.strftime('%Y-%m-%d') for date in list_of_dates]

            for formatted_date in formatted_dates:
                # iterating for
                print(formatted_date)

            raw_data_query = Q(l1_status="completed", l2_status="completed", l3_status="completed")

            if batchname_filter != "ALL":
                
                raw_data_query &= Q(baseid__batch_name=batchname_filter)

            raw_data_query &= Q(l1_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(l2_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(l3_prod__end_time__date__range=(fromdate, todate))

            raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                    'baseid__batch_name',         
                    'l1_emp__employeeName',
                    'l1_emp__employeeID',
                    'l2_emp__employeeID',
                    'l1_loc',
                    'l2_emp__employeeName',
                    'l2_loc',
                    'id_value', 
                    'question', 
                    'asin', 
                    'title', 
                    'product_url', 
                    'imagepath', 
                    'evidence', 
                    'answer_one', 
                    'answer_two',
                    'l1_status',
                    'l2_status',
                    'l4_status',
                    'l3_status',
                    'l1_l2_accuracy',
                    'l1_prod__que1',
                    'l1_prod__que2',
                    'l1_prod__que2_1',
                    'l1_prod__que3',
                    'l1_prod__is_present_both',
                    'l1_prod__que4_ans1',
                    'l1_prod__que5_ans1', 
                    'l1_prod__que6_ans1', 
                    'l1_prod__que7_ans1',
                    'l1_prod__que8_ans1',
                    'l1_prod__que9_ans1',
                    'l1_prod__que10_ans1',
                    'l1_prod__que11_ans1',
                    'l1_prod__q12_ans1',
                    'l1_prod__que4_ans2',
                    'l1_prod__que5_ans2',
                    'l1_prod__que6_ans2',
                    'l1_prod__que7_ans2',
                    'l1_prod__que8_ans2',
                    'l1_prod__que9_ans2',
                    'l1_prod__que10_ans2',
                    'l1_prod__que11_ans2',
                    'l1_prod__q12_ans2',
                    'l2_prod__que1',
                    'l2_prod__que2',
                    'l2_prod__que2_1',
                    'l2_prod__que3',
                    'l2_prod__is_present_both',
                    'l2_prod__que4_ans1',
                    'l2_prod__que5_ans1', 
                    'l2_prod__que6_ans1', 
                    'l2_prod__que7_ans1',
                    'l2_prod__que8_ans1',
                    'l2_prod__que9_ans1',
                    'l2_prod__que10_ans1',
                    'l2_prod__que11_ans1',
                    'l2_prod__q12_ans1',
                    'l2_prod__que4_ans2',
                    'l2_prod__que5_ans2',
                    'l2_prod__que6_ans2',
                    'l2_prod__que7_ans2',
                    'l2_prod__que8_ans2',
                    'l2_prod__que9_ans2',
                    'l2_prod__que10_ans2',
                    'l2_prod__que11_ans2',
                    'l2_prod__q12_ans2',
                    'l3_prod__que1',
                    'l3_prod__que2',
                    'l3_prod__que2_1',
                    'l3_prod__que3',
                    'l3_prod__is_present_both',
                    'l3_prod__que4_ans1',
                    'l3_prod__que5_ans1', 
                    'l3_prod__que6_ans1', 
                    'l3_prod__que7_ans1',
                    'l3_prod__que8_ans1',
                    'l3_prod__que9_ans1',
                    'l3_prod__que10_ans1',
                    'l3_prod__que11_ans1',
                    'l3_prod__q12_ans1',
                    'l3_prod__que4_ans2',
                    'l3_prod__que5_ans2',
                    'l3_prod__que6_ans2',
                    'l3_prod__que7_ans2',
                    'l3_prod__que8_ans2',
                    'l3_prod__que9_ans2',
                    'l3_prod__que10_ans2',
                    'l3_prod__que11_ans2',
                    'l3_prod__q12_ans2')



            result_df = pd.DataFrame(raw_data_values)

            new_columns_list = []

            # List of columns to compare
            columns_to_compare = [
                ('l1_prod__que1', 'l2_prod__que1', 'l3_prod__que1'),
                ('l1_prod__que2', 'l2_prod__que2', 'l3_prod__que2'),
                ('l1_prod__que2_1', 'l2_prod__que2_1', 'l3_prod__que2_1'),
                ('l1_prod__que3', 'l2_prod__que3', 'l3_prod__que3'),
                ('l1_prod__is_present_both', 'l2_prod__is_present_both', 'l3_prod__is_present_both'),
                ('l1_prod__que4_ans1', 'l2_prod__que4_ans1', 'l3_prod__que4_ans1'),
                ('l1_prod__que5_ans1', 'l2_prod__que5_ans1', 'l3_prod__que5_ans1'),
                ('l1_prod__que6_ans1', 'l2_prod__que6_ans1', 'l3_prod__que6_ans1'),
                ('l1_prod__que7_ans1', 'l2_prod__que7_ans1', 'l3_prod__que7_ans1'),
                ('l1_prod__que8_ans1', 'l2_prod__que8_ans1', 'l3_prod__que8_ans1'),
                ('l1_prod__que9_ans1', 'l2_prod__que9_ans1', 'l3_prod__que9_ans1'),
                ('l1_prod__que10_ans1', 'l2_prod__que10_ans1', 'l3_prod__que10_ans1'),
                ('l1_prod__que11_ans1', 'l2_prod__que11_ans1', 'l3_prod__que11_ans1'),
                ('l1_prod__q12_ans1', 'l2_prod__q12_ans1', 'l3_prod__q12_ans1'),
                ('l1_prod__que4_ans2', 'l2_prod__que4_ans2', 'l3_prod__que4_ans2'),
                ('l1_prod__que5_ans2', 'l2_prod__que5_ans2', 'l3_prod__que5_ans2'),
                ('l1_prod__que6_ans2', 'l2_prod__que6_ans2', 'l3_prod__que6_ans2'),
                ('l1_prod__que7_ans2', 'l2_prod__que7_ans2', 'l3_prod__que7_ans2'),
                ('l1_prod__que8_ans2', 'l2_prod__que8_ans2', 'l3_prod__que8_ans2'),
                ('l1_prod__que9_ans2', 'l2_prod__que9_ans2', 'l3_prod__que9_ans2'),
                ('l1_prod__que10_ans2', 'l2_prod__que10_ans2', 'l3_prod__que10_ans2'),
                ('l1_prod__que11_ans2', 'l2_prod__que11_ans2', 'l3_prod__que11_ans2'),
                ('l1_prod__q12_ans2', 'l2_prod__q12_ans2', 'l3_prod__q12_ans2'),
            ]

            # Loop through each set of three columns and perform the comparison
            for i, (col1, col2, col3) in enumerate(columns_to_compare):
                result_df[f'compare_{i}_l1_l2'] = result_df[col1] == result_df[col2]
                result_df[f'compare_{i}_l1_l3'] = result_df[col1] == result_df[col3]
                result_df[f'compare_{i}_l2_l3'] = result_df[col2] == result_df[col3]
                new_column_col = f'new_column_{i}'
                new_columns_list.append(new_column_col)
                # Add the values
                result_df[f'new_column_{i}'] = (
                    result_df[f'compare_{i}_l1_l2'].astype(int) +
                    result_df[f'compare_{i}_l1_l3'].astype(int) +
                    result_df[f'compare_{i}_l2_l3'].astype(int)
                )

            # Drop the intermediate comparison columns if needed
            result_df = result_df.drop(columns=[f'compare_{i}_l1_l2' for i in range(len(columns_to_compare))] +
                                            [f'compare_{i}_l1_l3' for i in range(len(columns_to_compare))] +
                                            [f'compare_{i}_l2_l3' for i in range(len(columns_to_compare))])

            
            result_df.loc['Total number of zeros'] = result_df[new_columns_list].eq(0).sum()
            result_df.loc['Total number of ones'] = result_df[new_columns_list].eq(1).sum()
            result_df.loc['Total number of threes'] = result_df[new_columns_list].eq(3).sum()

            result_df.loc['Total of above three'] = result_df.loc['Total number of zeros'] + result_df.loc['Total number of ones'] + result_df.loc['Total number of threes']
          
            result_df.loc['percentage'] = ((result_df.loc['Total number of ones'] + result_df.loc['Total number of threes']) / result_df.loc['Total of above three']) * 100

            percentage_df = pd.DataFrame(result_df.loc['percentage']).transpose()

            columns_to_remove = ['baseid__filename',
                    'baseid__batch_name',         
                    'l1_emp__employeeName',
                    'l1_emp__employeeID',
                    'l2_emp__employeeID',
                    'l1_loc',
                    'l2_emp__employeeName',
                    'l2_loc',
                    'id_value', 
                    'question', 
                    'asin', 
                    'title', 
                    'product_url', 
                    'imagepath', 
                    'evidence', 
                    'answer_one', 
                    'answer_two',
                    'l1_status',
                    'l2_status',
                    'l4_status',
                    'l3_status',
                    'l1_l2_accuracy',
                    'l1_prod__que1',
                    'l1_prod__que2',
                    'l1_prod__que2_1',
                    'l1_prod__que3',
                    'l1_prod__is_present_both',
                    'l1_prod__que4_ans1',
                    'l1_prod__que5_ans1', 
                    'l1_prod__que6_ans1', 
                    'l1_prod__que7_ans1',
                    'l1_prod__que8_ans1',
                    'l1_prod__que9_ans1',
                    'l1_prod__que10_ans1',
                    'l1_prod__que11_ans1',
                    'l1_prod__q12_ans1',
                    'l1_prod__que4_ans2',
                    'l1_prod__que5_ans2',
                    'l1_prod__que6_ans2',
                    'l1_prod__que7_ans2',
                    'l1_prod__que8_ans2',
                    'l1_prod__que9_ans2',
                    'l1_prod__que10_ans2',
                    'l1_prod__que11_ans2',
                    'l1_prod__q12_ans2',
                    'l2_prod__que1',
                    'l2_prod__que2',
                    'l2_prod__que2_1',
                    'l2_prod__que3',
                    'l2_prod__is_present_both',
                    'l2_prod__que4_ans1',
                    'l2_prod__que5_ans1', 
                    'l2_prod__que6_ans1', 
                    'l2_prod__que7_ans1',
                    'l2_prod__que8_ans1',
                    'l2_prod__que9_ans1',
                    'l2_prod__que10_ans1',
                    'l2_prod__que11_ans1',
                    'l2_prod__q12_ans1',
                    'l2_prod__que4_ans2',
                    'l2_prod__que5_ans2',
                    'l2_prod__que6_ans2',
                    'l2_prod__que7_ans2',
                    'l2_prod__que8_ans2',
                    'l2_prod__que9_ans2',
                    'l2_prod__que10_ans2',
                    'l2_prod__que11_ans2',
                    'l2_prod__q12_ans2',
                    'l3_prod__que1',
                    'l3_prod__que2',
                    'l3_prod__que2_1',
                    'l3_prod__que3',
                    'l3_prod__is_present_both',
                    'l3_prod__que4_ans1',
                    'l3_prod__que5_ans1', 
                    'l3_prod__que6_ans1', 
                    'l3_prod__que7_ans1',
                    'l3_prod__que8_ans1',
                    'l3_prod__que9_ans1',
                    'l3_prod__que10_ans1',
                    'l3_prod__que11_ans1',
                    'l3_prod__q12_ans1',
                    'l3_prod__que4_ans2',
                    'l3_prod__que5_ans2',
                    'l3_prod__que6_ans2',
                    'l3_prod__que7_ans2',
                    'l3_prod__que8_ans2',
                    'l3_prod__que9_ans2',
                    'l3_prod__que10_ans2',
                    'l3_prod__que11_ans2',
                    'l3_prod__q12_ans2']

            percentage_df = percentage_df.drop(columns=columns_to_remove)

            percentage_df.reset_index(inplace=True)

            melted_percentage_df = pd.melt(percentage_df)

            print(melted_percentage_df['value'])

            csv_data = result_df.to_csv(index=True, encoding='utf-8')
            
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'
            return response
        
        except Exception as e:
            return render(request, 'pages/iaa.html', {'batchname':batchname})

    return render(request, 'pages/iaa.html', {'batchname':batchname})


def iaa_date_wise(date):
    return ''
