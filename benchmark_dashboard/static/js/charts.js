$(function () {
    $(document).ready(function () {
        draw_charts('#cpu', 'http://localhost:5000/charts/1');
        draw_charts('#memory_transfer', 'http://localhost:5000/charts/2');
        draw_charts('#memory_ops_per_second', 'http://localhost:5000/charts/3');
        draw_charts('#data_disk_4k_rand_write', 'http://localhost:5000/charts/4');
        draw_charts('#data_disk_64k_seq_read', 'http://localhost:5000/charts/5');



    });
});





