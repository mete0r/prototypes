const path = require('path');
const appdir = path.resolve(__dirname, 'METE0R_PACKAGE')
const outdir = path.resolve(appdir, 'static')

const ManifestPlugin = require('webpack-manifest-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');



module.exports = {
    entry: {
        site: './METE0R_PACKAGE/templates/site.js',
        theme: './METE0R_PACKAGE/templates/theme.scss',
    },
    output: {
        path: outdir,
        filename: '[name].[hash].js',
    },
    optimization: {
        runtimeChunk: {
            name: 'runtime',
        },
        splitChunks: {
            chunks: 'all',
            cacheGroups: {
                commons: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all',
                },
            },
        },
    },
    module: {
        rules: [{
            test: /[.](js|jsx)$/,
            include: [
                path.resolve(appdir, 'templates'),
            ],
            exclude: /node_modules/,
            use: [{
                loader: 'babel-loader',
                options: {
                    presets: ['env'],
                },
            }, {
                loader: 'eslint-loader',
                options: {
                    failOnWarning: true,
                },
            }],
        }, {
            test: /[.]scss$/,
            include: [
                path.resolve(appdir, 'templates'),
            ],
            use: [{
                loader: MiniCssExtractPlugin.loader,
            },
            'css-loader',
            'sass-loader',
            ]
        }]
    },
    devtool: 'source-map',
    plugins: [
        new CleanWebpackPlugin([
            outdir,
        ]),
        new MiniCssExtractPlugin({
            filename: "[name].[hash].css",
        }),
        new ManifestPlugin(),
    ],
}
