# -*- coding: utf-8 -*-
import os

from django.core.files import File
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase

from eloue.products.models import Picture, Product, ProductReview, PatronReview

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


class ProductTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product']
    
    @transaction.commit_on_success
    def test_product_creation(self):
        product = Product(
            summary="Perceuse visseuse Philips",
            deposit_amount=250,
            description=u"Engrenage planétaire à haute performance 2 vitesses : durée de vie supérieure, transmission optimale, fonctionnement régulier.",
            address_id=1,
            quantity=1,
            category_id=35,
            owner_id=1
        )
        product.save()
    

class PictureTest(TestCase):
    def test_ensure_delete(self):
        f = open(local_path('../fixtures/bentley.jpg'))
        picture = Picture.objects.create(image=File(f))
        image_path = picture.image.path
        self.assertTrue(os.path.exists(image_path))
        picture.delete()
        self.assertFalse(os.path.exists(image_path))
    

class ProductReviewTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'booking']
    
    def test_score_values_negative(self):
        review = ProductReview(score=-1.0, product_id=1, description='Incorrect', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_too_high(self):
        review = ProductReview(score=2.0, product_id=1, description='Parfait', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_correct(self):
        try:
            review = ProductReview(score=0.5, product_id=1, description='Correct', reviewer_id=2)
            review.full_clean()
        except ValidationError, e:
            self.fail(e)
    
    def test_owner_review(self):
        review = ProductReview(score=2.0, product_id=1, description='Parfait', reviewer_id=1)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_booking_review(self):
        review = ProductReview(score=2.0, product_id=2, description='Parfait', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    

class PatronReviewTest(TestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'booking']
    
    def test_score_values_negative(self):
        review = PatronReview(score=-1.0, patron_id=1, description='Incorrect', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_too_high(self):
        review = PatronReview(score=2.0, patron_id=1, description='Parfait', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_correct(self):
        try:
            review = PatronReview(score=0.5, patron_id=1, description='Correct', reviewer_id=2)
            review.full_clean()
        except ValidationError, e:
            self.fail(e)
    
    def test_patron_review(self):
        review = PatronReview(score=2.0, patron_id=1, description='Correct', reviewer_id=1)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_booking_review(self):
        review = PatronReview(score=2.0, patron_id=2, description='Correct', reviewer_id=1)
        self.assertRaises(ValidationError, review.full_clean)
    
