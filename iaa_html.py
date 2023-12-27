{% extends "layouts/base.html" %}
{% load static %}
{% block title %} {% endblock %}

<!-- Specific CSS goes HERE -->
{% block stylesheets %}

{% endblock stylesheets %}
{% block content %}
{% load tags %}
<div class="grid-margin">
    <div class="card shadow">
        <div class="card-body">
            <div class="row">
                <div class="col-md-12 col-sm-12">
                    <form class="row mb-2" action="{% url 'iaa' %}" method="POST">
                        <input type="text" name="key" id="key" value="GetItem" style="display: none;">
                        {% csrf_token %}


                        <div class="col-md-2 col-sm-12">
                            <label for="fromdate">From Date</label>
                           
                                <input type="date" name="fromdate" id="fromdate" class="form-control"
                                    placeholder="From Date" required>
                           
                        </div>

                        <div class="col-md-2 col-sm-12">
                            <label for="todate">To Date</label>

                                <input type="date" name="todate" id="todate" class="form-control"
                                    placeholder="From Date" required>
                           
                        </div>

                        <div class="col-md-2 col-sm-12">
                            <label for="">batchname</label>

                            <select class="form-control select-form" name="batchname" id="batchname"
                                style="border: 1px solid black;color: black;" required>
                                <option value="">-- select --</option>
                                <option value="ALL">ALL</option>
                                {% for f in batchname %}
                                <option value="{{ f.batch_name }}">{{ f.batch_name }}</option>
                                {% endfor %}                                
                            </select>
                        </div>

                        <div class="col-md-2 col-sm-12">
                            <div class="mt-4">
                                <button class="btn btn-sm btn-success" id="storebtn">Get</button>
                            </div>
                        </div>
                    </form>
                    <div class="col-md-2 col-sm-12">
                        <div class="mt-4">
                            <button  id="submitBtn" class="btn btn-info">Download as csv</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <br>
    {% if tabledata %}
    <div class="card shadow-sm">
        <div class="card-body">
            <div class="table-responsive" style="overflow-y: scroll;max-height: 65vh;">
                {{ tabledata|safe }}
            </div>
        </div>
    </div>
    {% endif %}
</div>


    
<script src="{% static 'js/jquery_plugin.js' %}"></script>
<!-- Add this in the <head> section of your HTML -->
    <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>

<script>
    $("#storebtn").click(function () {
        localStorage.setItem('from', $("#fromdate").val());
        localStorage.setItem('to', $("#todate").val());
        localStorage.setItem('batchname', $("#batchname").val());
    })

    $("#submitBtn").click(function () {
        
        var formData = {
            csrfmiddlewaretoken:'{{ csrf_token }}',
            fromdate: localStorage.getItem('from'),
            todate: localStorage.getItem('to'),
            batchname: localStorage.getItem('batchname'),
            key: "Download"
        };

        // Send AJAX request
        $.ajax({
            type: "POST",
            url: "/api/v5/iaa/",
            data: formData,
            // dataType: 'json',
            success: function (response) {
                var a = document.createElement('a');
                a.href = 'data:attachment/csv,' + encodeURI(response);
                a.target = '_blank';
                a.download = 'IAA.csv';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            },
            error: function (error) {
                console.log(error);
            }
        });           
    });
   
</script>
{% endblock content %}
