# -*- coding: utf-8 -*-

from odoo import http
from datetime import timedelta, datetime


class ProductProduct(http.Controller):
    @http.route("/incoming_products/data", type="json", auth="user")
    def get_incoming_products(self):
        """function for getting incoming products"""

        data = http.request.env['stock.move.line'].search_read(
            [('qty_done', '>', 0),
             ('picking_id.picking_type_id.code', '=', 'incoming')],
            ['product_id', 'qty_done'])
        print(data)
        merged_data = {}
        for item in data:
            product_id = item['product_id']
            qty_done = item['qty_done']
            if product_id in merged_data:
                merged_data[product_id]['qty_done'] += qty_done
            else:
                merged_data[product_id] = item

        result = list(merged_data.values())
        sorted_products = sorted(result,
                                 key=lambda x: x['qty_done'], reverse=True)
        return sorted_products

    @http.route("/outgoing_products/data", type="json", auth="user")
    def get_outgoing_products(self):
        """function for getting outgoing products"""

        data = http.request.env['stock.move.line'].search_read(
            [('qty_done', '>', 0),
             ('picking_id.picking_type_id.code', '=', 'outgoing')],
            ['product_id', 'qty_done'])
        merged_data = {}
        for item in data:
            product_id = item['product_id']
            qty_done = item['qty_done']
            if product_id in merged_data:
                merged_data[product_id]['qty_done'] += qty_done
            else:
                merged_data[product_id] = item

        result = list(merged_data.values())
        sorted_products = sorted(result,
                                 key=lambda x: x['qty_done'], reverse=True)

        return sorted_products

    @http.route("/warehouse/data", type="json", auth="user")
    def get_warehouse(self):
        """functing for warehouse details"""

        return http.request.env['stock.warehouse'].search_read(
            [('company_id', '=', http.request.env.user.company_id.id)],
            ['name', 'lot_stock_id'])

    @http.route("/location/data", type="json", auth="user")
    def get_location_data(self):
        """function for getting location and available stock data"""

        locations = http.request.env['stock.location'].search_read(
            [('company_id', '=', http.request.env.user.company_id.id)],
            ['complete_name'])
        for location in locations:
            location['stock_count'] = http.request.env[
                'stock.quant'].search_count(
                [('location_id', '=', location.get('id'))])
        return locations

    @http.route('/internal-transfer/data', type='json', auth='user')
    def get_internal_transfer_data(self):
        """function for getting internal transfer data"""

        query = """
               SELECT sp.name AS picking_name, sm.name AS move_name, 
               sl_from.complete_name AS location_from, sl_dest.complete_name 
               AS location_dest, sp.id AS data_key FROM stock_picking AS sp
               LEFT JOIN stock_move AS sm ON sp.id = sm.picking_id
               LEFT JOIN stock_picking_type AS spt ON sp.picking_type_id = spt.id
               LEFT JOIN stock_location AS sl_from ON sl_from.id = sp.location_id
               LEFT JOIN stock_location AS sl_dest ON 
               sl_dest.id = sp.location_dest_id WHERE spt.code = 'internal' AND 
               sp.name IS NOT NULL;
           """
        http.request.env.cr.execute(query)
        data = http.request.env.cr.fetchall()
        return data

    @http.route("/stock-picking/data", type='json', auth='user')
    def get_stock_picking_data(self):
        """function for getting stock picking data"""

        user = http.request.env.user
        has_group = user.has_group('inventory_dashboard.inventory_manager')
        if has_group:
            return http.request.env['stock.picking'].search_read(
                [],
                ['name', 'location_id', 'location_dest_id', 'partner_id',
                 'company_id', 'picking_type_id'])
        else:
            return http.request.env['stock.picking'].search_read(
                [('create_uid', '=', user.id)],
                ['name', 'location_id', 'location_dest_id', 'partner_id',
                 'company_id', 'picking_type_id'])

    @http.route('/stock-picking-type/data', type='json', auth='user')
    def get_stock_picking_type_data(self):
        """function for getting stock picking types"""

        return http.request.env['stock.picking.type'].search_read(
            [('company_id', '=', http.request.env.user.company_id.id)],
            ['display_name'])

    @http.route("/inventory-value/data", type='json', auth='user')
    def get_inventory_valuation_data(self):
        """function for getting inventory valuation data"""

        records = http.request.env[
            'stock.valuation.layer'].sudo().search_read(
            [], ['value'])
        total_amount = sum(record['value'] for record in records)
        rounded_amount = round(total_amount, 2)
        return rounded_amount

    @http.route("/product-average-price/data", type='json', auth='user')
    def get_product_average_price_data(self):
        """function for getting product average price"""

        return http.request.env[
            'stock.valuation.adjustment.lines'].sudo().search_read(
            [], ['product_id', 'former_cost', 'additional_landed_cost',
                 'final_cost', 'quantity'])

    @http.route("/sort-last-week/data", type='json', auth='user')
    def get_last_week_data(self):
        """function for fetching last week data"""

        current_datetime = datetime.today() + timedelta(days=4)

        week_before = current_datetime - timedelta(days=7)
        records = http.request.env[
            'stock.valuation.layer'].sudo().search_read(
            [('create_date', '>=',
              week_before.strftime('%Y-%m-%d %H:%M:%S')),
             ('create_date', '<=',
              current_datetime.strftime('%Y-%m-%d %H:%M:%S'))],
            ['value']
        )
        total_amount = sum(record['value'] for record in records)
        rounded_amount = round(total_amount, 2)
        user = http.request.env.user
        has_group = user.has_group('inventory_dashboard.inventory_manager')
        if has_group:
            record = http.request.env['stock.picking'].search_read(
                [('scheduled_date', '>=',
                  week_before.strftime('%Y-%m-%d %H:%M:%S')), (
                     'scheduled_date', '<=',
                     current_datetime.strftime('%Y-%m-%d %H:%M:%S'))],
                ['name', 'location_id', 'location_dest_id', 'partner_id',
                 'company_id', 'picking_type_id'])
        else:
            record = http.request.env['stock.picking'].search_read(
                [('scheduled_date', '>=',
                  week_before.strftime('%Y-%m-%d %H:%M:%S')),
                 ('scheduled_date', '<=',
                  current_datetime.strftime('%Y-%m-%d %H:%M:%S')),
                 ('partner_id', '=', http.request.env.user.partner_id.id)],
                ['name', 'location_id', 'location_dest_id', 'partner_id',
                 'company_id', 'picking_type_id', 'scheduled_date']
            )
        data_in = http.request.env['stock.move.line'].search_read(
            [('date', '>=', week_before.strftime('%Y-%m-%d %H:%M:%S')),
             ('date', '<=', current_datetime.strftime('%Y-%m-%d %H:%M:%S')),
             ('qty_done', '>', 0),
             ('picking_id.picking_type_id.code', '=', 'incoming'),

             ],
            ['product_id', 'qty_done', 'date'])
        merged_data_in = {}
        for item in data_in:
            product_id = item['product_id']
            qty_done = item['qty_done']
            if product_id in merged_data_in:
                merged_data_in[product_id]['qty_done'] += qty_done
            else:
                merged_data_in[product_id] = item

        result = list(merged_data_in.values())
        product_in = sorted(result,
                            key=lambda x: x['qty_done'], reverse=True)
        data_out = http.request.env['stock.move.line'].search_read(
            [('qty_done', '>', 0),
             ('picking_id.picking_type_id.code', '=', 'outgoing'),
             ('date', '>=',
              week_before.strftime('%Y-%m-%d %H:%M:%S')),
             ('date', '<=',
              current_datetime.strftime('%Y-%m-%d %H:%M:%S'))],
            ['product_id', 'qty_done'])
        merged_data_out = {}
        for item in data_out:
            product_id = item['product_id']
            qty_done = item['qty_done']
            if product_id in merged_data_out:
                merged_data_out[product_id]['qty_done'] += qty_done
            else:
                merged_data_out[product_id] = item

        result_out = list(merged_data_out.values())
        product_out = sorted(result_out,
                             key=lambda x: x['qty_done'], reverse=True)

        data = {
            'total_amount': rounded_amount,
            'record': record,
            'product_in': product_in,
            'product_out': product_out,
        }
        return data

    @http.route("/sort-last-month/data", type='json', auth='user')
    def get_last_month_data(self):
        """function for getting last month data"""

        current_datetime = datetime.today()
        week_before = current_datetime - timedelta(days=30)
        records = http.request.env[
            'stock.valuation.layer'].sudo().search_read(
            [('create_date', '>=',
              week_before.strftime('%Y-%m-%d %H:%M:%S')),
             ('create_date', '<=',
              current_datetime.strftime('%Y-%m-%d %H:%M:%S'))],
            ['value']
        )
        total_amount = sum(record['value'] for record in records)
        rounded_amount = round(total_amount, 2)
        user = http.request.env.user
        has_group = user.has_group('inventory_dashboard.inventory_manager')
        if has_group:
            record = http.request.env['stock.picking'].search_read(
                [('scheduled_date', '>=',
                  week_before.strftime('%Y-%m-%d %H:%M:%S')), (
                     'scheduled_date', '<=',
                     current_datetime.strftime('%Y-%m-%d %H:%M:%S'))],
                ['name', 'location_id', 'location_dest_id', 'partner_id',
                 'company_id', 'picking_type_id'])
        else:
            record = http.request.env['stock.picking'].search_read(
                [('scheduled_date', '>=',
                  week_before.strftime('%Y-%m-%d %H:%M:%S')),
                 ('scheduled_date', '<=',
                  current_datetime.strftime('%Y-%m-%d %H:%M:%S')),
                 ('partner_id', '=', http.request.env.user.partner_id.id)],
                ['name', 'location_id', 'location_dest_id', 'partner_id',
                 'company_id', 'picking_type_id']

            )
        data_in = http.request.env['stock.move.line'].search_read(
            [('qty_done', '>', 0),
             ('picking_id.picking_type_id.code', '=', 'incoming'),
             ('date', '>=',
              week_before.strftime('%Y-%m-%d %H:%M:%S')),
             ('date', '<=',
              current_datetime.strftime('%Y-%m-%d %H:%M:%S'))],
            ['product_id', 'qty_done'])
        merged_data_in = {}
        for item in data_in:
            product_id = item['product_id']
            qty_done = item['qty_done']
            if product_id in merged_data_in:
                merged_data_in[product_id]['qty_done'] += qty_done
            else:
                merged_data_in[product_id] = item

        result = list(merged_data_in.values())
        product_in = sorted(result,
                            key=lambda x: x['qty_done'], reverse=True)

        data_out = http.request.env['stock.move.line'].search_read(
            [('qty_done', '>', 0),
             ('picking_id.picking_type_id.code', '=', 'outgoing'),
             ('date', '>=',
              week_before.strftime('%Y-%m-%d %H:%M:%S')),
             ('date', '<=',
              current_datetime.strftime('%Y-%m-%d %H:%M:%S'))],
            ['product_id', 'qty_done'])
        merged_data_out = {}
        for item in data_out:
            product_id = item['product_id']
            qty_done = item['qty_done']
            if product_id in merged_data_out:
                merged_data_out[product_id]['qty_done'] += qty_done
            else:
                merged_data_out[product_id] = item

        result_out = list(merged_data_out.values())
        product_out = sorted(result_out,
                             key=lambda x: x['qty_done'], reverse=True)

        data = {
            'total_amount': rounded_amount,
            'record': record,
            'product_in': product_in,
            'product_out': product_out,
        }
        return data
