"""View module for handling requests for customer data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer
from django.contrib.auth.models import User




class ServiceTicketView(ViewSet):
    """Honey Rae API Ticket view"""
    def destroy (self, request, pk=None):
        ticket = ServiceTicket.objects.get(pk=pk)
        ticket.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)



    def list(self, request):
        """Handle GET requests to get all Tickets

        Returns:
            Response -- JSON serialized list of Ticket
        """
        service_tickets = []


        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()

            if "status" in request.query_params:
                if request.query_params['status'] == "done":
                    service_tickets = service_tickets.filter(date_completed__isnull=False)

                if request.query_params['status'] == "all":
                    pass

        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """Handle GET requests for single customer

        Returns:
            Response -- JSON serialized customer record
        """

        ticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(ticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)
    

    
    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        #Select the targeted ticket using pk
        ticket = ServiceTicket.objects.get(pk=pk)

        #Get the employee id from the client request
        employee_id = request.data['employee']

        #Select the employee from the database using that id
        assigned_employee = Employee.objects.get(pk=employee_id)

        #Assign that employee to the employee property of th. ticket
        ticket.employee = assigned_employee
        ticket.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    
class TicketEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name')

class TicketCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'address', 'full_name')

class ServiceTicketSerializer(serializers.ModelSerializer):
    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)


    class Meta:
        model = ServiceTicket
        fields = ('id', 'customer', 'employee', 'description', 'emergency', 'date_completed')
        depth = 1

