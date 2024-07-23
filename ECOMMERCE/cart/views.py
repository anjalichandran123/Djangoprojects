from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from shop.models import Product
from cart.models import Cart
from cart.models import Payment
from cart.models import Order_table
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import razorpay


@login_required
def add_to_cart(request,pk):
    p=Product.objects.get(id=pk)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=p)
        if(p.stock>0):
            cart.quantity+=1
            cart.save()
            p.stock-=1
            p.save()

    except:
        if(p.stock):
            cart=Cart.objects.create(product=p,user=u,quantity=1)
            cart.save()
            p.stock-=1
            p.save()

    return redirect('cart:cart_views')


@login_required
def cart_views(request):
    u=request.user
    cart=Cart.objects.filter(user=u)
    total=0
    for i in cart:
        total=total+i.quantity*i.product.price
    return render(request,'cart_view.html',{'cart':cart,'total':total})


@login_required
def cart_decrement(request,pk):
    p=Product.objects.get(id=pk)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=p)
        if(cart.quantity>1):
            cart.quantity-=1
            cart.save()
            p.stock+=1
            p.save()
        else:
            cart.delete()
            p.stock+=1
            p.save()

    except:
        pass

    return cart_views(request)

@login_required
def delete(request,pk):
    p=Product.objects.get(id=pk)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=p)
        cart.delete()
        p.stock+=cart.quantity
        p.save()

    except:
        pass

    return redirect('cart:cart_views')


def place_order(request):
    if(request.method=='POST'):
        ph=request.POST.get('phone')
        a=request.POST.get('address')
        pin=request.POST.get('pin')


        u=request.user
        c=Cart.objects.filter(user=u)



        total=0
        for i in c:
            total=total+(i.quantity*i.product.price)
        print(total)#total amount of cart
        total=int(total*100)
        print(total)
        # create razor pay client using ourAPI  credentails
        client=razorpay.Client(auth=('rzp_test_qHyxGMysuy97Oy','mvOyHcNl9QuNbPFhYSzT6mPl'))

        #create order in razorpay
        response_payment=client.order.create(dict(amount=total,currency="INR"))

        print(response_payment)
        order_id=response_payment['id']
        order_status=response_payment['status']
        if order_status=="created":
            p=Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()

            for i in c:
                o = Order_table.objects.create(user=u, product=i.product, address=a, phone=ph, pin=pin,
                                               no_of_items=i.quantity, order_id=order_id)
                o.save()

            response_payment['name']=u.username
        return render(request, 'payment.html',{'payment':response_payment})

    return render(request,'place_order.html')

@csrf_exempt
def status(request,u):
    print(request.user.is_authenticated)   #false
    if not request.user.is_authenticated:
        user= User.objects.get(username=u)
        login(request,user)
        print(request.user.is_authenticated) #true

    if(request.method=="POST"):
        response=request.POST
        print(response)
        print(u)

        param_dict={
        'razorpay_order_id':response['razorpay_order_id'],
        'razorpay_payment_id':response['razorpay_payment_id'],
        'razorpay_signature':response['razorpay_signature']
        }

        client = razorpay.Client(auth=('rzp_test_qHyxGMysuy97Oy', 'mvOyHcNl9QuNbPFhYSzT6mPl'))

    try:
        status=client.utility.verify_payment_signature(param_dict)     #to check the authenticity of razorpay signature
        print(status)

        ord = Payment.objects.get(order_id=response['razorpay_order_id'])
        ord.razorpay_payment = response['razorpay_payment_id']
        ord.paid = True
        ord.save()

        u=User.objects.get(username=u)
        c=Cart.objects.filter(user=u)

        #filter trhe order_table details for particular user with order_id=respons['razorpay_order_id']
        o=Order_table.objects.filter(user=u,order_id=response['razorpay_order_id'])
        for i in o:
            i.payment_status="paid"    #edit paymentstatus paid
            i.save()

        c.delete()
        return render(request,'status.html',{'status':True})

    except:
        return render(request, 'status.html', {'status': False})


    return render(request,'status.html')


@login_required

def order_view(request):
    u=request.user
    customer=Order_table.objects.filter(user=u,payment_status="paid")

    return render(request,'order_view.html',{'customer':customer,'u':u.username})