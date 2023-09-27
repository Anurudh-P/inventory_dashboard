/** @odoo-module */
import { registry} from '@web/core/registry'
const { Component, useState} = owl
let chart_in = null;
let chart_out = null;
export class InventoryDashboard extends Component {
    setup(){
        super.setup()
        this.getStockIncoming()
        this.getStockOutgoing()
        this.getWarehouse()
        this.getLocationInfo()
        this.getInternalTransferInfo()
        this.getStockPickingInfo()
        this.getStockPickingTypeInfo()
        this.getInventoryValue()
        this.getProductAveragePrice()
        this.state = useState({
        incoming_product_data: [],
        outgoing_product_data: [],
        warehouse_data: [],
        location_data: [],
        internal_transfer_data: [],
        stock_picking_data: [],
        stock_picking_type_data: [],
        inventory_value_data:[],
        product_average_price_data: [],
    })
    }

    async getStockIncoming() {
        const rpc = this.env.services.rpc
        const data= await rpc("/incoming_products/data")
        this.state.incoming_product_data = data
        const ctx = document.getElementById("stockIncomingChart").getContext("2d");
        const labels = data.map((item) => item.product_id[1]);
        const incomingQty = data.map((item) => item.qty_done);
        if (chart_in != null){
            chart_in.destroy();
            }
        chart_in = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Incoming Quantity",
                        data: incomingQty,
                        backgroundColor: "rgba(75, 192, 192, 0.2)",
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }


    async getStockOutgoing() {
        const rpc = this.env.services.rpc
        const data= await rpc("/outgoing_products/data")
        this.state.outgoing_product_data = data
        const ctx = document.getElementById("stockOutgoingChart").getContext("2d");
        const labels = data.map((item) => item.product_id[1]);
        const outgoingQty = data.map((item) => item.qty_done);
        if (chart_out!=null){
            chart_out.destroy();
            }
            chart_out = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                    {
                        label: "Outgoing Quantity",
                        data: outgoingQty,
                        backgroundColor: "rgba(75, 192, 192, 0.2)",
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }
    async getWarehouse() {
        const rpc = this.env.services.rpc
        const data = await rpc("/warehouse/data")
        this.state.warehouse_data = data
    }
    async getLocationInfo() {
        const rpc = this.env.services.rpc
        const data = await rpc("/location/data")
        this.state.location_data = data
        const ctx = document.getElementById("stockLocationChart").getContext("2d");
        const labels = data.map((item) => item.complete_name);
        const Stock = data.map((item) => item.stock_count);
        new Chart(ctx, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Location and Stock",
                        data: Stock,
                        backgroundColor: ["rgba(255, 99, 132, 0.2)",
                                          "rgba(255, 206, 86, 0.2)",
                                          "rgba(75, 192, 192, 0.2)",
                                          "rgba(54, 162, 235, 0.2)",
                                          "rgba(153, 102, 255, 0.2)",
                                          "rgba(255, 159, 64, 0.2)",
                                          "rgba(255, 0, 0, 0.2)",
                                          "rgba(0, 255, 0, 0.2)",
                                          "rgba(0, 0, 255, 0.2)",
                                          "rgba(255, 99, 71, 0.2)",
                                          "rgba(255, 165, 0, 0.2)",
                                          "rgba(50, 205, 50, 0.2)",
                                          "rgba(128, 0, 128, 0.2)",],
                        borderColor: ["rgba(75, 192, 192, 1)", "rgba(255, 99, 132, 1)", "rgba(255, 206, 86, 1)"],
                        borderWidth: 1,
                    },
                ],
            },
            options: {

                },

        });

    }
    async getInternalTransferInfo(){
        const rpc = this.env.services.rpc
        const data = await rpc("/internal-transfer/data")
        this.state.internal_transfer_data = data
    }
    async getStockPickingInfo(){
        const rpc = this.env.services.rpc
        const data = await rpc("/stock-picking/data")
        this.state.stock_picking_data = data
    }
    async getStockPickingTypeInfo(){
        const rpc = this.env.services.rpc
        const data = await rpc("/stock-picking-type/data")
        this.state.stock_picking_type_data = data
    }
    async onChangePeriod(){
        var inputValue = document.getElementById('period-selection').value;
        const rpc = this.env.services.rpc
        if (inputValue === 'last_week'){
            const data = await rpc("/sort-last-week/data")

            this.state.inventory_value_data = data.total_amount
            this.state.stock_picking_data = data.record
            this.state.incoming_product_data = data.product_in
            this.state.outgoing_product_data= data.product_out

            const ctx = document.getElementById("stockIncomingChart").getContext("2d");
            const labels = data.product_in.map((item) => item.product_id[1]);
            const incomingQty = data.product_in.map((item) => item.qty_done);
            if (chart_in!=null){
                chart_in.destroy();
            }
            chart_in=new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Incoming Quantity",
                            data: incomingQty,
                            backgroundColor: "rgba(75, 192, 192, 0.2)",
                            borderColor: "rgba(75, 192, 192, 1)",
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                        },
                    },
                },
            });


            const ctxt = document.getElementById("stockOutgoingChart").getContext("2d");
            const label = data.product_out.map((item) => item.product_id[1]);
            const outgoingQty = data.product_out.map((item) => item.qty_done);
            if (chart_out!=null){
                 chart_out.destroy();
            }
            chart_out=new Chart(ctxt, {
                type: "bar",
                data: {
                    labels: label,
                    datasets: [
                        {
                            label: "Outgoing Quantity",
                            data: outgoingQty,
                            backgroundColor: "rgba(75, 192, 192, 0.2)",
                            borderColor: "rgba(75, 192, 192, 1)",
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                        },
                    },
                },
            });
        }
        else if (inputValue === 'last_month'){
            const data = await rpc("/sort-last-month/data")
            this.state.inventory_value_data = data.total_amount
            this.state.stock_picking_data = data.record
            this.state.incoming_product_data = data.product_in
            this.state.outgoing_product_data= data.product_out

            const ctx = document.getElementById("stockIncomingChart").getContext("2d");
            const labels = data.product_in.map((item) => item.product_id[1]);
            const incomingQty = data.product_in.map((item) => item.qty_done);
            if (chart_in != null){
            chart_in.destroy();
            }
            chart_in = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Incoming Quantity",
                            data: incomingQty,
                            backgroundColor: "rgba(75, 192, 192, 0.2)",
                            borderColor: "rgba(75, 192, 192, 1)",
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                        },
                    },
                },
            });
            const ctxt = document.getElementById("stockOutgoingChart").getContext("2d");
            const label = data.product_out.map((item) => item.product_id[1]);
            const outgoingQty = data.product_out.map((item) => item.qty_done);
            if (chart_out != null){
                chart_out.destroy();
            }
            new Chart(ctxt, {
                type: "bar",
                data: {
                    labels: label,
                    datasets: [
                        {
                            label: "Outgoing Quantity",
                            data: outgoingQty,
                            backgroundColor: "rgba(75, 192, 192, 0.2)",
                            borderColor: "rgba(75, 192, 192, 1)",
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                        },
                    },
                },
            });

        }
        else{
            this.getInventoryValue()
            this.getStockPickingInfo()
            this.getStockIncoming()
            this.getStockOutgoing()
        }
    }
    async getInventoryValue(){
        const rpc = this.env.services.rpc
        const data = await rpc("/inventory-value/data")
        this.state.inventory_value_data = data
    }
    async getProductAveragePrice(){
        const rpc = this.env.services.rpc
        const data = await rpc("/product-average-price/data")
        this.state.product_average_price_data = data
    }
}
InventoryDashboard.template = "inventory_dashboard_template"
registry.category("actions").add("inventory_dashboard_tag", InventoryDashboard)
