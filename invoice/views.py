from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.serializers import serialize
from django.http.response import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, renderers, mixins, decorators, response
from .models import Invoice, InvoiceItem, ItemsInInvoice, Transaction, Company
from .forms import InvoiceCreationForm, InvoiceChangeForm, InvoiceDeleteForm,\
    InvoiceItemCreationForm, InvoiceItemChangeForm, InvoiceItemDeleteForm,\
    TransactionCreationForm, TransactionChangeForm, TransactionDeleteForm
from .serializers import InvoiceSerializer, InvoiceItemSerializer, ItemsInInvoiceSerializer, TransactionSerializer, CompanySerializer
import json

from companies.url_variables import APPLICATION_NAME, URL_NAMES, URL_PATHS, Full_URL_PATHS_WITHOUT_ARGUMENTS, URL_NAMES_PREFIXED_WITH_APP_NAME
from companies.url_variables import *

# html generator
from companies.utils import get_field_names_from_model
from companies.html_generator import generate_template_tag_for_model, generate_data_container_table
from companies.repr_formats import HTML_Generator, Forms as FK_Formats

from .helper_functions import get_amount_for_invoice

from rest_framework.authentication import SessionAuthentication, BasicAuthentication 

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


application_name = APPLICATION_NAME
# these path names will be passed to templates to use in the navbar links
URLS = {
  'home': f'{application_name}:home',

  **Full_URL_PATHS_WITHOUT_ARGUMENTS.get_dict(),
  **URL_NAMES_PREFIXED_WITH_APP_NAME.get_dict()
}



class InvoiceViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):
    renderer_classes = [renderers.JSONRenderer]
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]

    @decorators.action(detail=False, methods=['get'])
    def home(self, request, *args, **kwargs):
        pk_field = 'id'
        exclude_fields = []
        include_fields = []
        keep_include_fields = True
        show_others = True
        model_fields = get_field_names_from_model(Invoice)
        # model_fields.append('incomplete_tasks')
        # model_fields = get_field_names_from_model(Invoice)
        context = {
            **URLS,
            'create_url': '/invoice/invoices/create_form/',
            'export_url': '/invoice/invoices/export/',

            'caption': 'View Invoice',
            'page_title': 'View Invoice',
            'template_tag': generate_template_tag_for_model(Invoice, pk_field=pk_field, show_id=True, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),
            'data_container': generate_data_container_table(Invoice, pk_field=pk_field, show_id=True, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),

            "counts": True,
            "invoice_counts": True,
            "invoice_overdue": Invoice.objects.all().count(),

            'frontend_data':{
            'all_url': '/invoice/invoices/all/',
            'search_url':  '/invoice/invoices/search/',
            'update_url':  r'/invoice/invoices/{pk}/update_form/',
            'delete_url':  r'/invoice/invoices/{pk}/delete_form/',
            'model_fields': model_fields
            },
        }
        return render(request, 'invoice/home.html', context)

    @decorators.action(detail=False, methods=['get', 'post'])
    def create_form(self, request, *args, **kwargs):
        context = {
            **URLS,
            'view_url': '/invoice/invoices/home/',
            'create_url': '/invoice/invoices/create_form/',

            'page_title': 'Create Invoice',
            'form_title': 'Invoice Creation Form',
            'form': InvoiceCreationForm(initial={}),
        }

        if request.method == 'POST':
            form = InvoiceCreationForm(request.POST)
            context['form'] = form
            
            if form.is_valid():
                invoice = form.save(commit=False)
    
                if invoice.invoice_to.is_limited:
                    invoice.customer_email = invoice.invoice_to.limited.business_email or ''
                    invoice.billing_address = invoice.invoice_to.limited.business_address or ''
                else:
                    invoice.customer_email = invoice.invoice_to.selfassesment.personal_email or ''
                    invoice.billing_address = invoice.invoice_to.selfassesment.personal_address or ''
                invoice.save()

                return redirect(reverse('invoices-update-form', args=(invoice.id,)))
        return render(request, template_name='invoice/create.html', context=context)
    
    
    @decorators.action(detail=True, methods=['get', 'post'])
    def update_form(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {
            **URLS,
            'view_url': '/invoice/invoices/home/',
            'update_url': f'/invoice/invoices/{instance.id}/update_form/',

            'page_title': 'Update Invoice',
            'form_title': 'Invoice Update Form',
            'form': InvoiceChangeForm(instance=instance, initial={}),

            'data_for_invoice_items': {
                'invoice_item': {
                    'repr_format': r'{fields.name} Rate: {fields.rate} VAT: {fields.vat_percent}%',
                    'search': {
                        'url': '/invoice/invoice_items/search/',
                        'request_method': 'GET',
                    },
                    'all': {
                        'url': '/invoice/invoice_items/all/',
                        'request_method': 'GET',
                    },
                },
                'invoice_id': instance.id,
                'items_in_invoice': {
                    'create': {
                        'url': r'/invoice/items_in_invoice/add_invoice_item_to_invoice/?invoice_id={invoice_id}&invoice_item_id={invoice_item_id}',
                        'request_method': 'GET',
                    },
                    'update': {
                        'url': r'/invoice/items_in_invoice/{pk}/',
                        'request_method': 'PUT',
                    },
                    'delete': {
                        'url': r'/invoice/items_in_invoice/{pk}/',
                        'request_method': 'DELETE',
                    },
                    'all': {
                        'url': r'/invoice/items_in_invoice/search/?invoice_id={invoice_id}',
                        'request_method': 'GET',
                    }
                },
            }
        }

        if request.method == 'POST':
            form = InvoiceChangeForm(request.POST, instance=instance)
            context['form'] = form
            
            if form.is_valid():
                invoice = form.save(commit=False)
                invoice.amount = get_amount_for_invoice(invoice)
                invoice.save()

                form = InvoiceChangeForm(instance=invoice)
                context['form'] = form

        return render(request, template_name='invoice/invoice_update.html', context=context)
    
    @decorators.action(detail=True, methods=['get', 'post'])
    def delete_form(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {
            **URLS,
            'view_url': '/invoice/invoices/home/',
            'delete_url': f'/invoice/invoices/{instance.id}/delete_form/',

            'page_title': 'Delete Invoice',
            'form_title': 'Invoice Delete Form',
            'form': InvoiceDeleteForm(),
        }

        if request.method == 'POST':
            form = InvoiceDeleteForm(request.POST)
            context['form'] = form
            
            if form.is_valid():
                instance.delete()
                return redirect('invoices-home')
        return render(request, template_name='invoice/delete.html', context=context)
    
    @decorators.action(detail=True, methods=['get'])
    def formatted(self, request, *args, **kwargs):
        instance = self.get_object()
        return HttpResponse(json.dumps({'formatted': f"#{instance.id} To: {instance.invoice_to}"}), content_type='application/json')
    
    def search_queryset_with_request_params(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        query = request.query_params.get('q', None)
        if query is not None:
            Query = Q(invoice_to__selfassesment__client_name__icontains=query) |\
                    Q(invoice_to__limited__client_name__icontains=query)
            queryset = queryset.filter(Query)
        return queryset

    @decorators.action(detail=False, methods=['get'])
    def search(self, request, *args, **kwargs):
        queryset = self.search_queryset_with_request_params(request, *args, **kwargs)
        serializer = serialize(queryset=queryset, format='json')
        return HttpResponse(serializer, content_type='application/json')
    
    @decorators.action(detail=False, methods=['get'])
    def all(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serialize(queryset=queryset, format='json')
        return HttpResponse(serializer, content_type='application/json')

    def json_format_instance(self, instance):
        return {
                    'model': self.serializer_class.Meta.model._meta.model_name,
                    'pk': instance.id,
                    'fields': {
                        'formatted': f"#{instance.id} To: {instance.invoice_to}"
                    }
                }
    def json_queryset(self, queryset):
        return json.dumps([self.json_format_instance(company) for company in queryset])

    @decorators.action(detail=False, methods=['get'])
    def formatted_search(self, request, *args, **kwargs):
        queryset = self.search_queryset_with_request_params(request, *args, **kwargs)
        return HttpResponse(self.json_queryset(queryset), content_type='application/json')
    
    @decorators.action(detail=False, methods=['get'])
    def formatted_all(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return HttpResponse(self.json_queryset(queryset), content_type='application/json')



class InvoiceItemViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):
    renderer_classes = [renderers.JSONRenderer]
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=['get'])
    def home(self, request, *args, **kwargs):
        pk_field = 'id'
        exclude_fields = []
        include_fields = []
        keep_include_fields = True
        show_others = True
        model_fields = get_field_names_from_model(InvoiceItem)
        # model_fields.append('incomplete_tasks')
        # model_fields = get_field_names_from_model(Invoice)
        context = {
            **URLS,
            'create_url': '/invoice/invoice_items/create_form/',
            'export_url': '/invoice/invoice_items/export/',

            'caption': 'View Invoice Item',
            'page_title': 'View Invoice Item',
            'template_tag': generate_template_tag_for_model(InvoiceItem, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),
            'data_container': generate_data_container_table(InvoiceItem, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),

            "counts": True,
            "invoice_item_counts": True,
            "invoice_overdue": InvoiceItem.objects.all().count(),

            'frontend_data':{
            'all_url': '/invoice/invoice_items/all/',
            'search_url':  '/invoice/invoice_items/search/',
            'update_url':  r'/invoice/invoice_items/{pk}/update_form/',
            'delete_url':  r'/invoice/invoice_items/{pk}/delete_form/',
            'model_fields': model_fields
            },
        }
        return render(request, 'invoice/home.html', context)

    @decorators.action(detail=False, methods=['get', 'post'])
    def create_form(self, request, *args, **kwargs):
        context = {
            **URLS,
            'view_url': '/invoice/invoice_items/home/',
            'create_url': '/invoice/invoice_items/create_form/',

            'page_title': 'Create Invoice Item',
            'form_title': 'Invoice Item Creation Form',
            'form': InvoiceItemCreationForm(initial={}),
        }

        if request.method == 'POST':
            form = InvoiceItemCreationForm(request.POST)
            context['form'] = form
            
            if form.is_valid():
                invoice = form.save()
                return redirect('invoice_items-home')
        return render(request, template_name='invoice/create.html', context=context)
    
    @decorators.action(detail=True, methods=['get', 'post'])
    def update_form(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {
            **URLS,
            'view_url': '/invoice/invoice_items/home/',
            'update_url': f'/invoice/invoice_items/{instance.id}/update_form/',

            'page_title': 'Update Invoice Item',
            'form_title': 'Invoice Item Update Form',
            'form': InvoiceItemChangeForm(instance=instance, initial={}),
        }

        if request.method == 'POST':
            form = InvoiceItemChangeForm(request.POST, instance=instance)
            context['form'] = form
            
            if form.is_valid():
                invoice = form.save()
        return render(request, template_name='invoice/update.html', context=context)
    
    @decorators.action(detail=True, methods=['get', 'post'])
    def delete_form(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {
            **URLS,
            'view_url': '/invoice/invoice_items/home/',
            'delete_url': f'/invoice/invoice_items/{instance.id}/delete_form/',

            'page_title': 'Delete Invoice Item',
            'form_title': 'Invoice Item Delete Form',
            'form': InvoiceItemDeleteForm(),
        }

        if request.method == 'POST':
            form = InvoiceItemDeleteForm(request.POST)
            context['form'] = form
            
            if form.is_valid():
                instance.delete()
                return redirect('invoice_items-home')
        return render(request, template_name='invoice/delete.html', context=context)

    @decorators.action(detail=False, methods=['get'])
    def search(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        query = request.query_params.get('q', None)
        if query is not None:
            Query = Q(name__icontains=query) |\
                    Q(description__icontains=query)
            queryset = queryset.filter(Query)
        serializer = serialize(queryset=queryset, format='json')
        return HttpResponse(serializer, content_type='application/json')
    
    @decorators.action(detail=False, methods=['get'])
    def all(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serialize(queryset=queryset, format='json')
        return HttpResponse(serializer, content_type='application/json')


class ItemsInInvoiceViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):
    renderer_classes = [renderers.JSONRenderer]
    queryset = ItemsInInvoice.objects.all()
    serializer_class = ItemsInInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]

    @decorators.action(detail=False, methods=['get'])
    def add_invoice_item_to_invoice(self, request, *args, **kwargs):
        invoice_id = request.GET.get('invoice_id', None)
        invoice_item_id = request.GET.get('invoice_item_id', None)
        if invoice_id is not None and invoice_item_id is not None:
            try:
                invoice = Invoice.objects.get(id=invoice_id)
                invoice_item = InvoiceItem.objects.get(id=invoice_item_id)
            except:
                return HttpResponse(json.dumps({'detail': "Record with provided invoice_id or invoice_item_id not found"}), status=400, content_type='application/json')
            
            try:
                added_item_in_invoice = ItemsInInvoice(invoice_id=invoice, invoice_item_id=invoice_item)
                added_item_in_invoice.rate = invoice_item.rate
                added_item_in_invoice.vat_percent = invoice_item.vat_percent
                added_item_in_invoice.save()
            except:
                added_item_in_invoice = ItemsInInvoice.objects.get(invoice_id=invoice, invoice_item_id=invoice_item)

            response = {
                "model": "invoice.itemsininvoice",
                "pk": added_item_in_invoice.id,
                "fields": {
                    "invoice_id": invoice.id,
                    "invoice_item_id": invoice_item.id,
                    "quantity": added_item_in_invoice.quantity,
                    "rate": added_item_in_invoice.rate,
                    "vat_percent": added_item_in_invoice.vat_percent,
                }
            }
            return HttpResponse(json.dumps(response), content_type='application/json')
        return HttpResponse(json.dumps({'detail': "invoice_id and invoice_item_id required"}), status=400, content_type='application/json')

    @decorators.action(detail=False, methods=['get'])
    def search(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        invoice_id = request.query_params.get('invoice_id', '')
        invoice_id = invoice_id.strip()
        if invoice_id.isnumeric():
            invoice_id = int(invoice_id)
            queryset = queryset.filter(invoice_id=invoice_id)
        else:
            return HttpResponse(status=400)
        
        serializer = serialize(queryset=queryset, format='json')
        return HttpResponse(serializer, content_type='application/json')


class TransactionViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):
    renderer_classes = [renderers.JSONRenderer]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=['get'])
    def home(self, request, *args, **kwargs):
        pk_field = 'id'
        exclude_fields = []
        include_fields = ['all_transactions']
        keep_include_fields = True
        show_others = True
        model_fields = get_field_names_from_model(Transaction)
        model_fields.append('all_transactions')
        # model_fields = get_field_names_from_model(Invoice)
        context = {
            **URLS,
            'create_url': '/invoice/transactions/create_form/',
            'export_url': '/invoice/transactions/export/',

            'caption': 'View Transaction',
            'page_title': 'View Transaction',
            'template_tag': generate_template_tag_for_model(Transaction, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others,),
            'data_container': generate_data_container_table(Transaction, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),

            "counts": True,
            "transaction_counts": True,
            "invoice_overdue": Transaction.objects.all().count(),

            'frontend_data':{
            'all_url': '/invoice/transactions/all/',
            'search_url':  '/invoice/transactions/search/',
            'update_url':  r'/invoice/transactions/{pk}/update_form/',
            'delete_url':  r'/invoice/transactions/{pk}/delete_form/',
            'model_fields': model_fields
            },
        }
        return render(request, 'invoice/home.html', context)
    
    @decorators.action(detail=True, methods=['get'])
    def view_all_transactions_of_company(self, request, *args, **kwargs):
        context = {}
        return render(request, 'invoice/home.html', context)

    @decorators.action(detail=False, methods=['get', 'post'])
    def create_form(self, request, *args, **kwargs):
        context = {
            **URLS,
            'view_url': '/invoice/transactions/home/',
            'create_url': '/invoice/transactions/create_form/',

            'page_title': 'Create Transaction',
            'form_title': 'Transaction Creation Form',
            'form': TransactionCreationForm(initial={}),
        }

        if request.method == 'POST':
            form = TransactionCreationForm(request.POST)
            context['form'] = form
            
            if form.is_valid():
                invoice = form.save()
                return redirect('transactions-home')
        return render(request, template_name='invoice/create.html', context=context)
    
    @decorators.action(detail=True, methods=['get', 'post'])
    def update_form(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {
            **URLS,
            'view_url': '/invoice/transactions/home/',
            'update_url': f'/invoice/transactions/{instance.id}/update_form/',

            'page_title': 'Update Transaction',
            'form_title': 'Transaction Update Form',
            'form': TransactionChangeForm(instance=instance, initial={}),
        }

        if request.method == 'POST':
            form = TransactionChangeForm(request.POST, instance=instance)
            context['form'] = form
            
            if form.is_valid():
                invoice = form.save()
        return render(request, template_name='invoice/update.html', context=context)
    
    @decorators.action(detail=True, methods=['get', 'post'])
    def delete_form(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {
            **URLS,
            'view_url': '/invoice/transactions/home/',
            'delete_url': f'/invoice/transactions/{instance.id}/delete_form/',

            'page_title': 'Delete Transaction',
            'form_title': 'Transaction Delete Form',
            'form': TransactionDeleteForm(),
        }

        if request.method == 'POST':
            form = TransactionDeleteForm(request.POST)
            context['form'] = form
            
            if form.is_valid():
                instance.delete()
                return redirect('transactions-home')
        return render(request, template_name='invoice/delete.html', context=context)

    @decorators.action(detail=False, methods=['get'])
    def search(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        query = request.query_params.get('q', None)
        if query is not None:
            Query = Q(transaction_from__selfassesment__client_name__icontains=query) |\
                    Q(transaction_from__limited__client_name__icontains=query) |\
                    Q(transaction_type__iexact=query)
            queryset = queryset.filter(Query)
        serializer = serialize(queryset=queryset, format='json')
        return HttpResponse(serializer, content_type='application/json')
    
    @decorators.action(detail=False, methods=['get'])
    def all(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serialize(queryset=queryset, format='json')
        return HttpResponse(serializer, content_type='application/json')
    

class CompanyViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):
    renderer_classes = [renderers.JSONRenderer]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=True, methods=['get'])
    def redirect_to_original(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_limited:
            pk = instance.limited.id
            return redirect(f"/companies/LTD/update/{pk}/")
        else:
            pk = instance.selfassesment.id
            return redirect(f"/companies/SA/update/{pk}/")

    @decorators.action(detail=True, methods=['get'])
    def formatted(self, request, *args, **kwargs):
        instance = self.get_object()
        # serializer = self.get_serializer(instance)
        return HttpResponse(json.dumps({'formatted': str(instance)}), content_type='application/json')

    def search_queryset_with_request_params(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        query = request.query_params.get('q', None)
        if query is not None:
            Query = Q(selfassesment__client_name__icontains=query) |\
                    Q(limited__client_name__icontains=query)
            queryset = queryset.filter(Query)
        return queryset

    def json_format_instance(self, instance):
        return {
                    'model': self.serializer_class.Meta.model._meta.model_name,
                    'pk': instance.id,
                    'fields': {
                        'formatted': str(instance)
                    }
                }
    def json_queryset(self, queryset):
        return json.dumps([self.json_format_instance(company) for company in queryset])

    @decorators.action(detail=False, methods=['get'])
    def formatted_search(self, request, *args, **kwargs):
        queryset = self.search_queryset_with_request_params(request, *args, **kwargs)
        return HttpResponse(self.json_queryset(queryset), content_type='application/json')
    
    @decorators.action(detail=False, methods=['get'])
    def formatted_all(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return HttpResponse(self.json_queryset(queryset), content_type='application/json')
    
    @decorators.action(detail=False, methods=['get'])
    def search(self, request, *args, **kwargs):
        queryset = self.search_queryset_with_request_params(request, *args, **kwargs)
        serializer = serialize(queryset=queryset, format='json')
        return HttpResponse(serializer, content_type='application/json')
    
    @decorators.action(detail=False, methods=['get'])
    def all(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = queryset.all()
        serializer = serialize(queryset=queryset, format='json')
        return HttpResponse(serializer, content_type='application/json')
    
