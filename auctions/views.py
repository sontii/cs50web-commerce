from auctions.forms import CreateListForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *

def index(request):  
    if request.user.is_authenticated:
        badge = wlist.objects.filter(user=request.user).count()
    else:
        badge = None
    auctionwoncount = listings.objects.filter(winner=request.user, active=False).count()
    auctionwon = None
    if auctionwoncount == 0:
        auctionwoncount = None
    else:
        auctionwon = listings.objects.filter(winner=request.user, active=False)

    return render(request, "auctions/index.html",{
        "auctionwon": auctionwon,
        "lists": listings.objects.filter(active=True),
        "badge": badge,
    })


@login_required(login_url='/login')
def categories(request):
    category = listings.objects.filter(active=True).order_by().values('category').distinct()
    
    return render(request, "auctions/categories.html",{
        "category": category,
    })

@login_required(login_url='/login')
def categories_list(request, category):
    lists = listings.objects.filter(category=category)
    cnt = listings.objects.filter(category=category).count()
    # list for category = None
    if cnt == 0:
        lists = listings.objects.filter(category__isnull=True)
    
    return render(request, "auctions/categories_list.html",{
        "category": category,
        "lists": lists,
    })

def item(request, item):
    # vars
    pk = listings.objects.filter(name=item).values('id')[0]['id']
    lastbid = bids.objects.filter(item=pk).values_list('user', flat=True).last()
    listeduserpk = listings.objects.filter(name=item).values('user')[0]['user']
    # closed action?
    active = listings.objects.filter(name=item).values('active')[0]['active']
    if active == True:
        active = True
    else:
        active = None
    try:
        winner = User.objects.filter(id=lastbid).values('username')[0]['username']
    except:
        winner = None

    if request.user.is_authenticated:
        badge = wlist.objects.filter(user=request.user).count()
        
        # to watchlist button
        if pk is not None:
            onthelist = wlist.objects.filter(user=request.user, item=pk).count()
            if onthelist == 0:
                onthelist = None

        # check user for close auction
        ownlist = listings.objects.filter(name=item, user = request.user).count()
        if ownlist == 0:
            ownlist = None
        else:
            ownlist = True

    else:
        badge = None
        onthelist = None
        ownlist = None

    # place bid
    if request.method == "POST":
        if 'placebid' in request.POST:
            placebid = float(request.POST['placebid'])
            pricenow = (listings.objects.filter(name=item).values_list('bid', flat=True))
            pricenow = float(pricenow[0])
            if listeduserpk == request.user.id:
                messages.success(request, "Can't bid your own auction!")
                return HttpResponseRedirect(reverse("item", args=(item,)))
            else:
                if placebid > pricenow:
                    listings.objects.filter(id=pk).update(bid=placebid)
                    bidding2 = bids(user=request.user,
                        item=listings.objects.filter(id=pk).first(), bid=placebid)
                    bidding2.save()
                    messages.success(request, 'Your bid accepted!')
                    return HttpResponseRedirect(reverse("item", args=(item,)))
                else:
                    messages.success(request, 'Your bid lower than current price!')
                    return HttpResponseRedirect(reverse("item", args=(item,)))
                
        # add comment
        elif 'addcomment' in request.POST:
            addcomment = request.POST['addcomment']
            acomment = comments(user=request.user,
                item=listings.objects.filter(id=pk).first(), comment=addcomment)
            acomment.save()
            messages.success(request, 'comment added')
            return HttpResponseRedirect(reverse("item", args=(item,)))

        # to watchlist
        elif 'towatchlist' in request.POST:
            tolist = wlist(user=request.user,
                item=listings.objects.filter(id=pk).first())
            tolist.save()
            messages.success(request, 'added to your watchlist')
            return HttpResponseRedirect(reverse("item", args=(item,)))
        
        # remove from watchlist
        elif 'outwatchlist' in request.POST:
            tolist = wlist.objects.filter(user=request.user,
                item=listings.objects.filter(id=pk).first())
            tolist.delete()
            messages.success(request, 'Removed from your watchlist')
            return HttpResponseRedirect(reverse("item", args=(item,)))
        
        # close auction
        elif 'closeauction' in request.POST:
            if winner == None:
                listings.objects.filter(name=item).update(active=False)    
                messages.success(request, "Auction closed without winner")
                return HttpResponseRedirect(reverse("item", args=(item,)))
            
            listings.objects.filter(name=item).update(winner=winner, active=False)
            messages.success(request, 'Auction closed! winner is: ' + winner)
            return HttpResponseRedirect(reverse("item", args=(item,)))

    else:      
        #get object
        lists = listings.objects.filter(name=item)

        #count bids
        bid = bids.objects.filter(item=pk).count()
        
        currbid = listings.objects.filter(name=item).values_list('bid', flat=True)
        currbid = currbid[0]

        # if no bids on item
        bidder = None

        try:
            usrbid = bids.objects.filter(
                item=pk, user=request.user).values_list(
                    'bid', flat=True).latest('bid')
            if currbid == usrbid:
                bidder = "Your bid is the curent bid"
            else:
                bidder = None
        except:        
            usrbid = None
            
        comment = comments.objects.filter(item=pk)

        return render(request, "auctions/item.html",{
            "lists": lists,
            "badge": badge,
            "bid": bid,
            "usrbid": usrbid,
            "bidder": bidder,
            "comment": comment,
            "onthelist": onthelist,
            "ownlist" : ownlist,
            "active": active,
        })

@login_required(login_url='/login')
def watchlist(request):
    return render(request, "auctions/watchlist.html",{
        "lists": wlist.objects.filter(user=request.user),
        "badge": wlist.objects.filter(user=request.user).count()
    })

@login_required(login_url='/login')
def createlist(request):
    form = CreateListForm()
    if request.method == "POST":
        auction = listings(user=request.user, bid=request.POST['price'])
        form = CreateListForm(request.POST or None, request.FILES or None, instance=auction)
        if form.is_valid():
            form.save()
            form = CreateListForm()

        return render(request, "auctions/createlist.html",{
            "form": form,
            "badge": wlist.objects.filter(user=request.user).count()
        })

    else:
        return render(request, "auctions/createlist.html",{
            "form": form,
            "badge": wlist.objects.filter(user=request.user).count()
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
