const path = require('path');
const appdir = path.resolve(__dirname, 'src/METE0R_PACKAGE')
const outdir = path.resolve(appdir, 'static')

const { WebpackManifestPlugin } = require('webpack-manifest-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');


module.exports = {
    entry: {
        root: './src/METE0R_PACKAGE/templates/root.js',
        theme: './src/METE0R_PACKAGE/templates/theme.scss',
    },
    output: {
        path: outdir,

        // https://stackoverflow.com/questions/65245185/new-to-webpackautoprefix-problem-with-webpack-manifest-plugin
        // https://webpack.js.org/migrate/5/
        publicPath: "",

        filename: '[name].[contenthash].js',
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
            }],
        }, {
            test: /[.]scss$/,
            include: [
                path.resolve(appdir, 'templates'),
            ],
            use: [
                {
                    loader: MiniCssExtractPlugin.loader,
                },
                'css-loader',
                'postcss-loader',
                'sass-loader',
            ]
        }]
    },
    devtool: 'source-map',
    plugins: [
        new ESLintPlugin(),
        new CleanWebpackPlugin(),
        new MiniCssExtractPlugin({
            filename: "[name].[contenthash].css",
        }),
        new WebpackManifestPlugin(),
    ],
}
