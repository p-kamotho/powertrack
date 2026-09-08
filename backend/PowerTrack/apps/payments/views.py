from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import PaymentForm
from .models import Payment
from .services import record_payment


@login_required
def payment_list(request):
    payments = Payment.objects.select_related(
        "bill",
        "bill__tenant",
    )

    return render(
        request,
        "payments/payment_list.html",
        {"payments": payments},
    )


@login_required
def payment_create(request):
    form = PaymentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        payment_data = form.cleaned_data

        record_payment(
            bill=payment_data["bill"],
            amount=payment_data["amount"],
            method=payment_data["method"],
            reference=payment_data.get("reference", ""),
        )

        return redirect("payment_list")

    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": "Record Payment",
            "back": "payment_list",
        },
    )
